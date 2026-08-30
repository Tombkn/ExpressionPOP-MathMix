// ============================================================================
//  mathmix_lib.glsl  —  Math Mix POP operations as GLSL functions
//  for the Expression POP (Function Store). Inserted before main() by the
//  patched generator (script1_callbacks). Formulas follow TouchDesigner's own
//  generated code: https://docs.derivative.ca/Math_Mix_Combine_Functions
//
//  1:1 with the Math Mix "Operation" menu — EXCEPT:
//   • names that already exist in GLSL are NOT redefined (abs sign sqrt floor
//     round ceil fract normalize exp exp2 log2 sin cos tan asin acos atan
//     degrees radians length min max mod dot cross reflect refract mix clamp
//     smoothstep pow). Write them as GLSL: A ** B -> pow(A, B), ln(A) -> ln(A)
//     (defined here), 1 / A -> inv(A) ("inverse" is GLSL's matrix inverse).
//   • angles: Math-Mix-only functions keep Math Mix semantics = DEGREES
//     (atan2, angle, sind/cosd/... helpers). GLSL built-ins stay radians.
//     Radian twins: atan2rad, anglerad.
//   • int(A) -> trunc(A);  int(A / B) -> intdiv(A, B);  A if C else B -> ifelse(A, B, C)
//   • comparisons as functions (return 1.0 / 0.0): gt gte lt lte eq ne,
//     range checks: bltealtc = B <= A < C, bltaltec = B < A <= C,
//     bltaltc = B < A < C, bltealtec = B <= A <= C
//   • array functions (arrayadd, arraymult, arrayavg, arraymin, arraymax,
//     arraylength) are generated PER ATTRIBUTE by the generator, not here.
//   • dbtopow / powtodb / dbtoamp / amptodb use the standard audio formulas
//     (TD's exact definition is not documented).
// ============================================================================
#define MATHMIX_LIB 1

// ---------------------------------------------------------------- single A
float square(float a) { return a * a; }
vec2  square(vec2 a)  { return a * a; }
vec3  square(vec3 a)  { return a * a; }
vec4  square(vec4 a)  { return a * a; }

// 1 / A  — Math Mix: A != 0 ? 1/A : A
float inv(float a) { return (a != 0.0) ? 1.0 / a : a; }
vec2  inv(vec2 a)  { return vec2(inv(a.x), inv(a.y)); }
vec3  inv(vec3 a)  { return vec3(inv(a.x), inv(a.y), inv(a.z)); }
vec4  inv(vec4 a)  { return vec4(inv(a.x), inv(a.y), inv(a.z), inv(a.w)); }

float exp10(float a) { return pow(10.0, a); }
vec2  exp10(vec2 a)  { return pow(vec2(10.0), a); }
vec3  exp10(vec3 a)  { return pow(vec3(10.0), a); }
vec4  exp10(vec4 a)  { return pow(vec4(10.0), a); }

// log10 / ln — Math Mix returns A unchanged when A <= 0 (GLSL would give NaN)
float log10(float a) { return (a > 0.0) ? log(a) / log(10.0) : a; }
float ln(float a)    { return (a > 0.0) ? log(a) : a; }

// trig in DEGREES (Math Mix semantics). GLSL sin/cos/... stay radians.
float sind(float deg)  { return sin(radians(deg)); }
float cosd(float deg)  { return cos(radians(deg)); }
float tand(float deg)  { return tan(radians(deg)); }
float asind(float a)   { return (a >= -1.0 && a <= 1.0) ? degrees(asin(a)) : a; }
float acosd(float a)   { return (a >= -1.0 && a <= 1.0) ? degrees(acos(a)) : a; }
float atand(float a)   { return degrees(atan(a)); }

// dB conversions (standard audio formulas)
float dbtopow(float db)  { return pow(10.0, db / 10.0); }
float powtodb(float p)   { return (p > 0.0) ? 10.0 * log(p) / log(10.0) : 0.0; }
float dbtoamp(float db)  { return pow(10.0, db / 20.0); }
float amptodb(float amp) { return (amp > 0.0) ? 20.0 * log(amp) / log(10.0) : 0.0; }

// ------------------------------------------------- vector -> one number
float compadd(float a) { return a; }
float compadd(vec2 a)  { return a.x + a.y; }
float compadd(vec3 a)  { return a.x + a.y + a.z; }
float compadd(vec4 a)  { return a.x + a.y + a.z + a.w; }

float compsub(float a) { return a; }
float compsub(vec2 a)  { return a.x - a.y; }
float compsub(vec3 a)  { return a.x - a.y - a.z; }
float compsub(vec4 a)  { return a.x - a.y - a.z - a.w; }

float compmult(float a) { return a; }
float compmult(vec2 a)  { return a.x * a.y; }
float compmult(vec3 a)  { return a.x * a.y * a.z; }
float compmult(vec4 a)  { return a.x * a.y * a.z * a.w; }

// compdiv — Math Mix: result becomes 0 on division by 0
float compdiv(float a) { return a; }
float compdiv(vec2 a)  { return (a.y != 0.0) ? a.x / a.y : 0.0; }
float compdiv(vec3 a)  { float r = a.x; r = (a.y != 0.0) ? r / a.y : 0.0; r = (a.z != 0.0) ? r / a.z : 0.0; return r; }
float compdiv(vec4 a)  { float r = a.x; r = (a.y != 0.0) ? r / a.y : 0.0; r = (a.z != 0.0) ? r / a.z : 0.0; r = (a.w != 0.0) ? r / a.w : 0.0; return r; }

float compavg(float a) { return a; }
float compavg(vec2 a)  { return (a.x + a.y) * 0.5; }
float compavg(vec3 a)  { return (a.x + a.y + a.z) / 3.0; }
float compavg(vec4 a)  { return (a.x + a.y + a.z + a.w) * 0.25; }

float compmin(float a) { return a; }
float compmin(vec2 a)  { return min(a.x, a.y); }
float compmin(vec3 a)  { return min(a.x, min(a.y, a.z)); }
float compmin(vec4 a)  { return min(min(a.x, a.y), min(a.z, a.w)); }

float compmax(float a) { return a; }
float compmax(vec2 a)  { return max(a.x, a.y); }
float compmax(vec3 a)  { return max(a.x, max(a.y, a.z)); }
float compmax(vec4 a)  { return max(max(a.x, a.y), max(a.z, a.w)); }

// ---------------------------------------------------------------- A, B
// logB(A) — Math Mix: B != 0 && B != 1 && A != 0 ? log(A)/log(B) : 0
float logB(float a, float b) { return (b != 0.0 && b != 1.0 && a != 0.0) ? log(a) / log(b) : 0.0; }

float avg(float a, float b) { return 0.5 * (a + b); }
vec2  avg(vec2 a, vec2 b)   { return 0.5 * (a + b); }
vec3  avg(vec3 a, vec3 b)   { return 0.5 * (a + b); }
vec4  avg(vec4 a, vec4 b)   { return 0.5 * (a + b); }

// int(A / B)
float intdiv(float a, float b) { return trunc(a / b); }

// comparisons -> 1.0 / 0.0 (component-wise for vectors)
float gt(float a, float b)  { return float(a > b); }
float gte(float a, float b) { return float(a >= b); }
float lt(float a, float b)  { return float(a < b); }
float lte(float a, float b) { return float(a <= b); }
float eq(float a, float b)  { return float(a == b); }
float ne(float a, float b)  { return float(a != b); }
vec2  gt(vec2 a, vec2 b)    { return vec2(greaterThan(a, b)); }
vec3  gt(vec3 a, vec3 b)    { return vec3(greaterThan(a, b)); }
vec4  gt(vec4 a, vec4 b)    { return vec4(greaterThan(a, b)); }
vec2  gte(vec2 a, vec2 b)   { return vec2(greaterThanEqual(a, b)); }
vec3  gte(vec3 a, vec3 b)   { return vec3(greaterThanEqual(a, b)); }
vec4  gte(vec4 a, vec4 b)   { return vec4(greaterThanEqual(a, b)); }
vec2  lt(vec2 a, vec2 b)    { return vec2(lessThan(a, b)); }
vec3  lt(vec3 a, vec3 b)    { return vec3(lessThan(a, b)); }
vec4  lt(vec4 a, vec4 b)    { return vec4(lessThan(a, b)); }
vec2  lte(vec2 a, vec2 b)   { return vec2(lessThanEqual(a, b)); }
vec3  lte(vec3 a, vec3 b)   { return vec3(lessThanEqual(a, b)); }
vec4  lte(vec4 a, vec4 b)   { return vec4(lessThanEqual(a, b)); }
vec2  eq(vec2 a, vec2 b)    { return vec2(equal(a, b)); }
vec3  eq(vec3 a, vec3 b)    { return vec3(equal(a, b)); }
vec4  eq(vec4 a, vec4 b)    { return vec4(equal(a, b)); }
vec2  ne(vec2 a, vec2 b)    { return vec2(notEqual(a, b)); }
vec3  ne(vec3 a, vec3 b)    { return vec3(notEqual(a, b)); }
vec4  ne(vec4 a, vec4 b)    { return vec4(notEqual(a, b)); }
// tolerant equality (floats are rarely exactly equal)
float eqtol(float a, float b, float tol) { return float(abs(a - b) <= tol); }

// atan2(A, B) — A = y, B = x. Math Mix returns DEGREES.
float atan2(float y, float x)    { return degrees(atan(y, x)); }
float atan2rad(float y, float x) { return atan(y, x); }

// angle(A, B) — angle between vectors, DEGREES (Math Mix)
float angle(vec3 a, vec3 b) { float d = dot(a, b) / max(length(a) * length(b), 1.0e-12); return degrees(acos(clamp(d, -1.0, 1.0))); }
float angle(vec2 a, vec2 b) { float d = dot(a, b) / max(length(a) * length(b), 1.0e-12); return degrees(acos(clamp(d, -1.0, 1.0))); }
float anglerad(vec3 a, vec3 b) { return radians(angle(a, b)); }
float anglerad(vec2 a, vec2 b) { return radians(angle(a, b)); }

// ---------------------------------------------------------------- A, B, C
// rangefrom(A, B, C): A from [B, C] -> 0..1   (Math Mix: B != C ? (A-B)/(C-B) : A)
float rangefrom(float a, float b, float c) { return (b != c) ? (a - b) / (c - b) : a; }
vec2  rangefrom(vec2 a, float b, float c)  { return vec2(rangefrom(a.x, b, c), rangefrom(a.y, b, c)); }
vec3  rangefrom(vec3 a, float b, float c)  { return vec3(rangefrom(a.x, b, c), rangefrom(a.y, b, c), rangefrom(a.z, b, c)); }
vec4  rangefrom(vec4 a, float b, float c)  { return vec4(rangefrom(a.x, b, c), rangefrom(a.y, b, c), rangefrom(a.z, b, c), rangefrom(a.w, b, c)); }
vec2  rangefrom(vec2 a, vec2 b, vec2 c)    { return vec2(rangefrom(a.x, b.x, c.x), rangefrom(a.y, b.y, c.y)); }
vec3  rangefrom(vec3 a, vec3 b, vec3 c)    { return vec3(rangefrom(a.x, b.x, c.x), rangefrom(a.y, b.y, c.y), rangefrom(a.z, b.z, c.z)); }
vec4  rangefrom(vec4 a, vec4 b, vec4 c)    { return vec4(rangefrom(a.x, b.x, c.x), rangefrom(a.y, b.y, c.y), rangefrom(a.z, b.z, c.z), rangefrom(a.w, b.w, c.w)); }

// rangeto(A, B, C): 0..1 -> [B, C]   (A * (C - B) + B)
float rangeto(float a, float b, float c) { return a * (c - b) + b; }
vec2  rangeto(vec2 a, float b, float c)  { return a * (c - b) + b; }
vec3  rangeto(vec3 a, float b, float c)  { return a * (c - b) + b; }
vec4  rangeto(vec4 a, float b, float c)  { return a * (c - b) + b; }
vec2  rangeto(vec2 a, vec2 b, vec2 c)    { return a * (c - b) + b; }
vec3  rangeto(vec3 a, vec3 b, vec3 c)    { return a * (c - b) + b; }
vec4  rangeto(vec4 a, vec4 b, vec4 c)    { return a * (c - b) + b; }

// remap in one go: from [b, c] to [d, e]
float remap(float a, float b, float c, float d, float e) { return rangeto(rangefrom(a, b, c), d, e); }

// A if C else B   (Math Mix: mix(B, A, float(C > 0)))
float ifelse(float a, float b, float c) { return (c > 0.0) ? a : b; }
vec2  ifelse(vec2 a, vec2 b, float c)   { return (c > 0.0) ? a : b; }
vec3  ifelse(vec3 a, vec3 b, float c)   { return (c > 0.0) ? a : b; }
vec4  ifelse(vec4 a, vec4 b, float c)   { return (c > 0.0) ? a : b; }
vec2  ifelse(vec2 a, vec2 b, vec2 c)    { return mix(b, a, vec2(greaterThan(c, vec2(0.0)))); }   // component-wise C
vec3  ifelse(vec3 a, vec3 b, vec3 c)    { return mix(b, a, vec3(greaterThan(c, vec3(0.0)))); }
vec4  ifelse(vec4 a, vec4 b, vec4 c)    { return mix(b, a, vec4(greaterThan(c, vec4(0.0)))); }

// loop(A, B, C): sawtooth between B and C   (TD's TDLoop)
float loop(float a, float b, float c) { float v = (a - b) / (c - b); return mix(b, c, fract(v)); }
vec2  loop(vec2 a, float b, float c)  { return vec2(loop(a.x, b, c), loop(a.y, b, c)); }
vec3  loop(vec3 a, float b, float c)  { return vec3(loop(a.x, b, c), loop(a.y, b, c), loop(a.z, b, c)); }
vec4  loop(vec4 a, float b, float c)  { return vec4(loop(a.x, b, c), loop(a.y, b, c), loop(a.z, b, c), loop(a.w, b, c)); }
vec2  loop(vec2 a, vec2 b, vec2 c)    { return vec2(loop(a.x, b.x, c.x), loop(a.y, b.y, c.y)); }
vec3  loop(vec3 a, vec3 b, vec3 c)    { return vec3(loop(a.x, b.x, c.x), loop(a.y, b.y, c.y), loop(a.z, b.z, c.z)); }
vec4  loop(vec4 a, vec4 b, vec4 c)    { return vec4(loop(a.x, b.x, c.x), loop(a.y, b.y, c.y), loop(a.z, b.z, c.z), loop(a.w, b.w, c.w)); }

// zigzag(A, B, C): ping-pong between B and C   (TD's TDZigZag; parity test via float mod so it is
// also defined for A < B — GLSL's integer % is undefined for negative operands)
float zigzag(float a, float b, float c) {
    float v = (a - b) / (c - b);
    bool flip = mod(floor(v), 2.0) == 1.0;
    v = fract(v);
    if (flip) v = 1.0 - v;
    return mix(b, c, v);
}
vec2 zigzag(vec2 a, float b, float c) { return vec2(zigzag(a.x, b, c), zigzag(a.y, b, c)); }
vec3 zigzag(vec3 a, float b, float c) { return vec3(zigzag(a.x, b, c), zigzag(a.y, b, c), zigzag(a.z, b, c)); }
vec4 zigzag(vec4 a, float b, float c) { return vec4(zigzag(a.x, b, c), zigzag(a.y, b, c), zigzag(a.z, b, c), zigzag(a.w, b, c)); }
vec2 zigzag(vec2 a, vec2 b, vec2 c)   { return vec2(zigzag(a.x, b.x, c.x), zigzag(a.y, b.y, c.y)); }
vec3 zigzag(vec3 a, vec3 b, vec3 c)   { return vec3(zigzag(a.x, b.x, c.x), zigzag(a.y, b.y, c.y), zigzag(a.z, b.z, c.z)); }
vec4 zigzag(vec4 a, vec4 b, vec4 c)   { return vec4(zigzag(a.x, b.x, c.x), zigzag(a.y, b.y, c.y), zigzag(a.z, b.z, c.z), zigzag(a.w, b.w, c.w)); }

// range checks -> 1.0 / 0.0
float bltealtc(float a, float b, float c)  { return float(b <= a && a <  c); }   // B <= A <  C
float bltaltec(float a, float b, float c)  { return float(b <  a && a <= c); }   // B <  A <= C
float bltaltc(float a, float b, float c)   { return float(b <  a && a <  c); }   // B <  A <  C
float bltealtec(float a, float b, float c) { return float(b <= a && a <= c); }   // B <= A <= C

// ---------------------------------------------------------------- colour
vec3 RGBtoHSV(vec3 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}
vec4 RGBtoHSV(vec4 c) { return vec4(RGBtoHSV(c.rgb), c.a); }

vec3 HSVtoRGB(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
vec4 HSVtoRGB(vec4 c) { return vec4(HSVtoRGB(c.rgb), c.a); }
// ============================================================================
