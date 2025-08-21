// ./src/knot_pd.cpp
#include "knot_pd.h"
#include <cmath>
#include <algorithm>
#include <optional>
#include <random>
#include <stdexcept>

namespace vam {

static inline double dot3(const Vec3& a, const Vec3& b){
  return a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
}
static inline Vec3 cross3(const Vec3& a, const Vec3& b){
  return { a[1]*b[2]-a[2]*b[1],
          a[2]*b[0]-a[0]*b[2],
          a[0]*b[1]-a[1]*b[0] };
}
static inline double norm3(const Vec3& a){ return std::sqrt(dot3(a,a)); }

static inline Vec3 unit_random_dir(std::mt19937& rng){
  std::normal_distribution<double> N(0.0,1.0);
  Vec3 v{N(rng),N(rng),N(rng)};
  const double n = norm3(v) + 1e-18;
  return {v[0]/n, v[1]/n, v[2]/n};
}

static inline void orthonormal_basis(const Vec3& n, Vec3& u, Vec3& v){
  const Vec3 a = (std::abs(n[0]) < 0.9) ? Vec3{1.0,0.0,0.0} : Vec3{0.0,1.0,0.0};
  u = cross3(n, a);
  const double un = norm3(u) + 1e-18;
  u = {u[0]/un, u[1]/un, u[2]/un};
  v = cross3(n, u);
}

static inline void project_curve(const std::vector<Vec3>& P3,
                                 const Vec3& n,
                                 std::vector<Vec2>& P2,
                                 std::vector<double>& D)
{
  Vec3 u, v;
  orthonormal_basis(n, u, v);
  const size_t N = P3.size();
  P2.resize(N);
  D.resize(N);
  for(size_t i=0;i<N;++i){
    const Vec3& p = P3[i];
    P2[i] = { dot3(p,u), dot3(p,v) };
    D[i]  =  dot3(p,n);
  }
}

static inline std::optional<std::pair<double,double>>
seg_intersection(const Vec2& p1, const Vec2& p2,
                 const Vec2& q1, const Vec2& q2,
                 double eps = 1e-12)
{
  const double x1=p1[0], y1=p1[1];
  const double x2=p2[0], y2=p2[1];
  const double x3=q1[0], y3=q1[1];
  const double x4=q2[0], y4=q2[1];
  const double den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4);
  if(std::abs(den) < eps) return std::nullopt;

  const double lam = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / den;
  const double mu  = ((x1-x3)*(y1-y2) - (y1-y3)*(x1-x2)) / den;

  if(lam <= eps || lam >= 1.0-eps) return std::nullopt;
  if(mu  <= eps || mu  >= 1.0-eps) return std::nullopt;
  return std::make_pair(lam, mu);
}

static std::vector<Crossing> build_pd_from_projection(
    const std::vector<Vec2>& P2,
    const std::vector<double>& D,
    double min_angle_deg,
    double depth_tol)
{
  const int N = static_cast<int>(P2.size());
  struct CrossingGeom { int i,j; double lam,mu; bool over_i; };
  std::vector<CrossingGeom> crosses;

  for(int i=0;i<N;++i){
    const Vec2& p1 = P2[i];
    const Vec2& p2 = P2[(i+1)%N];
    for(int j=i+2;j<N;++j){
      if(j==i || j==(i-1+N)%N || (i==0 && j==N-1)) continue;
      const Vec2& q1 = P2[j];
      const Vec2& q2 = P2[(j+1)%N];
      auto ans = seg_intersection(p1,p2,q1,q2);
      if(!ans) continue;

      const double lam = ans->first, mu = ans->second;
      const double Di = D[i] + lam*(D[(i+1)%N]-D[i]);
      const double Dj = D[j] + mu*(D[(j+1)%N]-D[j]);
      if(std::abs(Di - Dj) < depth_tol) continue;

      const double dxi = p2[0]-p1[0], dyi = p2[1]-p1[1];
      const double dxj = q2[0]-q1[0], dyj = q2[1]-q1[1];
      const double dotv = dxi*dxj + dyi*dyj;
      const double ni = std::hypot(dxi, dyi) + 1e-18;
      const double nj = std::hypot(dxj, dyj) + 1e-18;
      double cosang = dotv/(ni*nj);
      cosang = std::max(-1.0, std::min(1.0, cosang));
      const double ang = std::acos(std::abs(cosang))*180.0/3.14159265358979323846;
      if(ang < min_angle_deg) continue;

      crosses.push_back({i,j,lam,mu,(Di>Dj)});
    }
  }
  if(crosses.empty()) throw std::runtime_error("No crossings detected (projection not generic).");

  struct Event { double s; int cross_id; bool over; int in_lab; int out_lab; };
  std::vector<Event> ev;
  ev.reserve(crosses.size()*2);
  for(int cid=0; cid<(int)crosses.size(); ++cid){
    const auto& c = crosses[cid];
    ev.push_back({ (c.i + c.lam)/double(N), cid,  c.over_i, 0,0 });
    ev.push_back({ (c.j + c.mu )/double(N), cid, !c.over_i, 0,0 });
  }
  std::sort(ev.begin(), ev.end(), [](const Event& a, const Event& b){ return a.s < b.s; });
  for(size_t k=1;k<ev.size();++k){
    if(std::abs(ev[k].s - ev[k-1].s) < 1e-12) ev[k].s += 1e-9;
  }

  const int L = static_cast<int>(ev.size());
  for(int idx=0; idx<L; ++idx){
    ev[idx].in_lab  = (idx>0 ? idx : L);
    ev[idx].out_lab = (idx+1<=L ? idx+1 : 1);
  }

  std::vector<Crossing> pd; pd.reserve(crosses.size());
  for(int cid=0; cid<(int)crosses.size(); ++cid){
    int a=-1,b=-1,c=-1,d=-1;
    for(const auto& e : ev){
      if(e.cross_id != cid) continue;
      if(e.over){ b = e.in_lab; d = e.out_lab; }
      else      { a = e.in_lab; c = e.out_lab; }
    }
    if(a>0 && b>0 && c>0 && d>0) pd.push_back({a,b,c,d});
  }

  std::vector<int> counts(L+1,0);
  for(const auto& t : pd){ for(int lab : t) counts[lab]++; }
  for(int lab=1; lab<=L; ++lab){
    if(counts[lab] != 2)
      throw std::runtime_error("PD validation failed (labels must appear exactly twice).");
  }
  return pd;
}

PD pd_from_curve(const std::vector<Vec3>& P3,
                 int tries,
                 unsigned int seed,
                 double min_angle_deg,
                 double depth_tol)
{
  if(P3.size() < 4) throw std::invalid_argument("pd_from_curve: need at least 4 points");
  std::mt19937 rng(seed);
  PD best; int best_score = -1;

  for(int t=0; t<tries; ++t){
    const Vec3 n = unit_random_dir(rng);
    std::vector<Vec2> P2; std::vector<double> D;
    project_curve(P3, n, P2, D);
    try{
      PD pd = build_pd_from_projection(P2, D, min_angle_deg, depth_tol);
      const int score = (int)pd.size();
      if(score > best_score){ best_score = score; best = std::move(pd); }
    }catch(...){ /* try next */ }
  }
  if(best_score < 0) throw std::runtime_error("Failed to extract PD from any projection.");
  return best;
}

} // namespace vam
