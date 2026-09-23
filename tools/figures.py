"""Erzeugt die animierten Übungsfiguren (SVG + SMIL) für Eisenlog.

Jede Bewegung hat eine Start- (A) und Endpose (B). Gelenke werden per
2-Knochen-IK aus Hüfte, Rumpfwinkel und Hand-/Fußziel berechnet.
Ausgabe: JS-Objekt FIG {typ: svg}, eingefügt in index.html zwischen den Markern.
"""
import math, json, re, pathlib

T_SHO, T_HEAD, UA, FA, TH, SH, FOOT = 23, 31, 14, 13, 20, 19, 6
FLOOR = 94

def P(p, ang, L):  # Winkel in Grad, 90 = oben, 0 = vorne (rechts)
    a = math.radians(ang); return (p[0] + L * math.cos(a), p[1] - L * math.sin(a))

def ik(s, t, a, b, sign):
    dx, dy = t[0] - s[0], t[1] - s[1]; d = max(1e-3, min(math.hypot(dx, dy), a + b - 0.05))
    base = math.atan2(dy, dx); off = math.acos(max(-1, min(1, (a * a + d * d - b * b) / (2 * a * d))))
    ang = base + sign * off; j = (s[0] + a * math.cos(ang), s[1] + a * math.sin(ang))
    ang2 = math.atan2(t[1] - j[1], t[0] - j[0]); e = (j[0] + b * math.cos(ang2), j[1] + b * math.sin(ang2))
    return j, e

def rel(base, v):
    return (base[0] + v[1], base[1] + v[2]) if isinstance(v, tuple) and v and v[0] == 'rel' else v

def pose(p):
    hip = p['hip']; t = p['t']
    sho = P(hip, t, T_SHO); head = P(hip, t + p.get('hn', 0), T_HEAD)
    hand = rel(sho, p['hand']); elb, hand = ik(sho, hand, UA, FA, p.get('es', 1))
    foot = rel(hip, p['foot']); knee, ank = ik(hip, foot, TH, SH, p.get('ks', -1))
    toe = P(ank, p.get('ft', 0), FOOT)
    far = {}
    fh = rel(sho, p['fhand']) if 'fhand' in p else (hand[0] - 2.5, hand[1])
    far['elb'], far['hand'] = ik(sho, fh, UA, FA, p.get('fes', p.get('es', 1)))
    ff = rel(hip, p['ffoot']) if 'ffoot' in p else (foot[0] - 3, foot[1])
    far['knee'], far['ank'] = ik(hip, ff, TH, SH, p.get('fks', p.get('ks', -1)))
    far['toe'] = P(far['ank'], p.get('fft', p.get('ft', 0)), FOOT)
    return dict(hip=hip, sho=sho, head=head, elb=elb, hand=hand, knee=knee, ank=ank, toe=toe, far=far)

def front(p):  # Frontansicht: symmetrische Arme
    cx = 50; hip = (cx, 56); sho_r, sho_l = (cx + 9, 32), (cx - 9, 32)
    hr = p['hand']; hl = (2 * cx - hr[0], hr[1])
    er, hr2 = ik(sho_r, hr, UA, FA, p.get('es', -1)); el, hl2 = ik(sho_l, hl, UA, FA, -p.get('es', -1))
    return dict(front=True, hip=hip, sho_r=sho_r, sho_l=sho_l, er=er, hr=hr2, el=el, hl=hl2, head=(cx, 21))

f = lambda v: f'{v:.1f}'.rstrip('0').rstrip('.')
def pts(*ps): return 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in ps)

def parts(q, eq):
    """Liefert geordnete Teile: (tag, klasse, attr-dict) – nur diese Werte werden animiert."""
    out = []
    if q.get('front'):
        cx = 50
        out.append(('path', 'ff', {'d': pts((cx - 6, 57), (cx - 8, 75), (cx - 8, FLOOR))}))
        out.append(('path', 'fb leg', {'d': pts((cx + 6, 57), (cx + 8, 75), (cx + 8, FLOOR))}))
        out.append(('path', 'fb torso', {'d': pts((cx, 55), (cx, 33))}))
        out.append(('path', 'fb sh', {'d': pts(q['sho_l'], q['sho_r'])}))
        out.append(('circle', 'fh', {'cx': q['head'][0], 'cy': q['head'][1]}))
        out.append(('path', 'fb arm', {'d': pts(q['sho_r'], q['er'], q['hr'])}))
        out.append(('path', 'fb arm', {'d': pts(q['sho_l'], q['el'], q['hl'])}))
        if eq in ('db', 'bar'):
            for h in (q['hr'], q['hl']): out.append(('circle', 'fe db', {'cx': h[0], 'cy': h[1]}))
        return out
    fr = q['far']
    if eq == 'barsho': out.append(('circle', 'fe bar', {'cx': q['sho'][0] - 5, 'cy': q['sho'][1]}))
    out.append(('path', 'ff', {'d': pts(q['hip'], fr['knee'], fr['ank'], fr['toe'])}))
    out.append(('path', 'ff', {'d': pts(q['sho'], fr['elb'], fr['hand'])}))
    out.append(('path', 'fb torso', {'d': pts(q['hip'], q['sho'])}))
    out.append(('path', 'fb leg', {'d': pts(q['hip'], q['knee'], q['ank'], q['toe'])}))
    out.append(('circle', 'fh', {'cx': q['head'][0], 'cy': q['head'][1]}))
    out.append(('path', 'fb arm', {'d': pts(q['sho'], q['elb'], q['hand'])}))
    if eq == 'bar': out.append(('circle', 'fe bar', {'cx': q['hand'][0], 'cy': q['hand'][1]}))
    elif eq == 'db': out.append(('circle', 'fe db', {'cx': q['hand'][0], 'cy': q['hand'][1]}))
    elif eq == 'barhip': out.append(('circle', 'fe bar', {'cx': q['hip'][0], 'cy': q['hip'][1] - 7}))
    elif eq == 'pad': out.append(('circle', 'fe db', {'cx': q['ank'][0], 'cy': q['ank'][1]}))
    return out

KT = '0;0.38;0.5;0.88;1'
KS = ';'.join(['.45 0 .55 1'] * 4)
def anim(attr, a, b):
    if a == b: return ''
    return f'<animate attributeName="{attr}" values="{a};{b};{b};{a};{a}" keyTimes="{KT}" calcMode="spline" keySplines="{KS}" dur="3.2s" repeatCount="indefinite"></animate>'

def svg(spec):
    mk = front if spec.get('front') else pose
    qa, qb = mk(spec['A']), mk(spec['B'])
    eq = spec.get('eq', 'none')
    pa, pb = parts(qa, eq), parts(qb, eq)
    body = [f'<path class="fl" d="M6 {FLOOR + 1.5}H94"></path>']
    for m in spec.get('mach', []): body.append(f'<path class="fm" d="{m}"></path>')
    if 'cable' in spec:
        c = spec['cable']; ha = (qa['hr'] if qa.get('front') else qa['hand']); hb = (qb['hr'] if qb.get('front') else qb['hand'])
        da, db_ = pts(c, ha), pts(c, hb)
        body.append(f'<path class="fc" d="{da}">{anim("d", da, db_)}</path>')
        if qa.get('front'):
            c2 = (100 - c[0], c[1]); da, db_ = pts(c2, qa['hl']), pts(c2, qb['hl'])
            body.append(f'<path class="fc" d="{da}">{anim("d", da, db_)}</path>')
        body.append(f'<circle class="fp" cx="{f(c[0])}" cy="{f(c[1])}" r="3"></circle>')
    for (tag, cls, A), (_, _, B) in zip(pa, pb):
        if tag == 'path':
            body.append(f'<path class="{cls}" d="{A["d"]}">{anim("d", A["d"], B["d"])}</path>')
        else:
            ax, ay, bx, by = f(A['cx']), f(A['cy']), f(B['cx']), f(B['cy'])
            r = 5.5 if cls == 'fh' else 8 if 'bar' in cls else 4.2
            body.append(f'<circle class="{cls}" cx="{ax}" cy="{ay}" r="{r}">{anim("cx", ax, bx)}{anim("cy", ay, by)}</circle>')
    return '<svg viewBox="0 0 100 100" class="fig" aria-hidden="true">' + ''.join(body) + '</svg>'

S = lambda **k: k
STAND = S(hip=(50, 55), t=90, foot=(52, FLOOR), ks=-1)
BENCH = ['M16 67H70', 'M22 67V94', 'M64 67V94']
FIGS = {
 'bench': S(eq='bar', mach=BENCH, A=S(hip=(60, 62), t=180, hand=(40, 57), es=1, foot=(80, FLOOR), ks=1), B=S(hip=(60, 62), t=180, hand=(39, 36), es=1, foot=(80, FLOOR), ks=1)),
 'benchdb': S(eq='db', mach=BENCH, A=S(hip=(60, 62), t=180, hand=(33, 58), es=1, foot=(80, FLOOR), ks=1), B=S(hip=(60, 62), t=180, hand=(38, 36), es=1, foot=(80, FLOOR), ks=1)),
 'incline': S(eq='db', mach=['M14 54L62 72', 'M58 70V94', 'M24 58V94'], A=S(hip=(60, 66), t=152, hand=(44, 46), es=1, foot=(82, FLOOR), ks=1), B=S(hip=(60, 66), t=152, hand=(47, 25), es=1, foot=(82, FLOOR), ks=1)),
 'chestpress': S(eq='none', mach=['M26 74H50', 'M30 74L26 44', 'M40 74V94', 'M78 30V70'], A=S(hip=(38, 70), t=96, hand=(52, 44), es=1, foot=(60, FLOOR), ks=1), B=S(hip=(38, 70), t=96, hand=(72, 44), es=1, foot=(60, FLOOR), ks=1)),
 'fly': S(front=True, eq='none', mach=['M20 12V94', 'M80 12V94'], A=S(hand=(84, 34), es=1), B=S(hand=(54, 42), es=1)),
 'crossover': S(front=True, eq='none', cable=(90, 10), A=S(hand=(82, 28), es=1), B=S(hand=(53, 62), es=1)),
 'pushup': S(eq='none', A=S(hip=(58, 83), t=177, hand=(34, FLOOR), es=-1, foot=(92, FLOOR), ks=1, ft=-60), B=S(hip=(58, 71), t=172, hand=(34, FLOOR), es=-1, foot=(92, FLOOR), ks=1, ft=-60)),
 'dips': S(eq='none', mach=['M52 58V94', 'M44 58H60'], A=S(hip=(48, 66), t=100, hand=(52, 58), es=1, foot=(40, 94), ks=1, ffoot=(38, 92)), B=S(hip=(49, 50), t=94, hand=(52, 58), es=1, foot=(42, 86), ks=1, ffoot=(40, 84))),
 'ohp': S(eq='bar', A=dict(STAND, hand=(58, 30), es=1), B=dict(STAND, hand=(52, 6), es=1)),
 'ohpdb': S(eq='db', A=dict(STAND, hand=('rel', 4, -1), es=1), B=dict(STAND, hand=(51, 6), es=1)),
 'raise': S(front=True, eq='db', A=S(hand=(62, 58), es=-1), B=S(hand=(85, 33), es=-1)),
 'frontraise': S(eq='db', A=dict(STAND, hand=(52, 58), es=-1), B=dict(STAND, hand=(76, 30), es=-1)),
 'uprow': S(eq='bar', A=dict(STAND, hand=(53, 58), es=-1), B=dict(STAND, hand=(55, 30), es=-1)),
 'pushdown': S(eq='none', cable=(64, 6), A=dict(STAND, hand=(62, 40), es=-1), B=dict(STAND, hand=(56, 59), es=-1)),
 'overhead': S(eq='db', A=dict(STAND, hand=(44, 22), es=1), B=dict(STAND, hand=(50, 5), es=1)),
 'kickback': S(eq='db', A=S(hip=(38, 58), t=30, hand=(54, 62), es=-1, foot=(44, FLOOR)), B=S(hip=(38, 58), t=30, hand=(32, 48), es=-1, foot=(44, FLOOR))),
 'pullup': S(eq='none', mach=['M20 11H80', 'M22 11V94', 'M78 11V94'], A=S(hip=(50, 64), t=90, hand=(52, 12), es=1, foot=(46, 100), ks=1), B=S(hip=(50, 45), t=90, hand=(52, 12), es=1, foot=(44, 80), ks=1)),
 'legraise': S(eq='none', mach=['M20 11H80', 'M22 11V94', 'M78 11V94'], A=S(hip=(50, 64), t=90, hand=(52, 12), es=1, foot=(48, 100), ks=-1), B=S(hip=(50, 64), t=94, hand=(52, 12), es=1, foot=(88, 58), ks=-1)),
 'pulldown': S(eq='none', cable=(50, 3), mach=['M36 74H58', 'M60 64H72'], A=S(hip=(46, 72), t=92, hand=(50, 22), es=1, foot=(66, FLOOR), ks=1), B=S(hip=(46, 72), t=98, hand=(54, 40), es=1, foot=(66, FLOOR), ks=1)),
 'row': S(eq='bar', A=S(hip=(40, 56), t=32, hand=(60, 70), es=1, foot=(46, FLOOR)), B=S(hip=(40, 56), t=32, hand=(52, 58), es=1, foot=(46, FLOOR))),
 'rowdb': S(eq='db', mach=['M60 66H86', 'M64 66V94', 'M84 66V94'], A=S(hip=(38, 56), t=18, hand=('rel', 2, 20), es=1, foot=(40, FLOOR)), B=S(hip=(38, 56), t=18, hand=('rel', -8, 8), es=1, foot=(40, FLOOR))),
 'cablerow': S(eq='none', cable=(94, 58), mach=['M24 78H46', 'M76 66V92'], A=S(hip=(36, 74), t=80, hand=(66, 58), es=1, foot=(74, 84), ks=1), B=S(hip=(36, 74), t=96, hand=(48, 60), es=1, foot=(74, 84), ks=1)),
 'pullover': S(eq='none', cable=(88, 6), A=S(hip=(40, 56), t=70, hand=(72, 18), es=1, foot=(38, FLOOR)), B=S(hip=(40, 56), t=70, hand=(58, 60), es=1, foot=(38, FLOOR))),
 'deadlift': S(eq='bar', A=S(hip=(38, 68), t=40, hand=(58, 84), es=1, foot=(52, FLOOR), ks=1), B=dict(STAND, hand=(52, 60), es=1)),
 'rdl': S(eq='bar', A=S(hip=(42, 57), t=18, hand=(64, 80), es=1, foot=(46, FLOOR), ks=1), B=dict(STAND, hand=(52, 60), es=1)),
 'shrug': S(eq='bar', A=dict(STAND, hand=(52, 60), es=1), B=dict(STAND, hand=(52, 55), es=1)),
 'curl': S(eq='db', A=dict(STAND, hand=(53, 59), es=-1), B=dict(STAND, hand=(60, 34), es=-1)),
 'curlbar': S(eq='bar', A=dict(STAND, hand=(53, 59), es=-1), B=dict(STAND, hand=(60, 34), es=-1)),
 'cablecurl': S(eq='none', cable=(70, 92), A=dict(STAND, hand=(54, 59), es=-1), B=dict(STAND, hand=(60, 34), es=-1)),
 'facepull': S(eq='none', cable=(92, 24), A=dict(STAND, hand=(76, 28), es=-1), B=dict(STAND, hand=(58, 22), es=-1)),
 'squat': S(eq='barsho', A=S(hip=(38, 73), t=58, hand=('rel', -4, 4), es=-1, foot=(52, FLOOR), ks=1), B=dict(STAND, hand=('rel', -4, 4), es=-1)),
 'legpress': S(eq='none', mach=['M8 78L34 72', 'M12 76L2 50', 'M20 76V94'], A=S(hip=(30, 72), t=128, hand=(38, 74), es=1, foot=(54, 50), ks=-1, ft=60), B=S(hip=(30, 72), t=128, hand=(38, 74), es=1, foot=(66, 42), ks=-1, ft=60)),
 'lunge': S(eq='db', A=S(hip=(48, 71), t=90, hand=('rel', 1, 26), es=1, foot=(66, FLOOR), ks=1, ffoot=(30, FLOOR), fks=1, fft=-40), B=S(hip=(48, 56), t=90, hand=('rel', 1, 26), es=1, foot=(62, FLOOR), ks=1, ffoot=(34, FLOOR), fks=1, fft=-40)),
 'legext': S(eq='pad', mach=['M28 68H56', 'M32 68L28 38', 'M42 68V94'], A=S(hip=(40, 64), t=96, hand=(46, 68), es=1, foot=(60, 88), ks=-1, ft=0), B=S(hip=(40, 64), t=96, hand=(46, 68), es=1, foot=(78, 62), ks=-1, ft=80)),
 'legcurl': S(eq='pad', mach=['M14 72H78', 'M20 72V94', 'M72 72V94'], A=S(hip=(52, 66), t=180, hand=(24, 72), es=-1, foot=(90, 66), ks=1, ft=-90), B=S(hip=(52, 66), t=180, hand=(24, 72), es=-1, foot=(64, 42), ks=1, ft=-90)),
 'hipthrust': S(eq='barhip', mach=['M10 64H34', 'M16 64V94'], A=S(hip=(54, 84), t=152, hand=('rel', 16, 6), es=1, foot=(76, FLOOR), ks=1), B=S(hip=(56, 64), t=176, hand=('rel', 16, 0), es=1, foot=(76, FLOOR), ks=1)),
 'calf': S(eq='db', mach=['M44 90H70V95'], A=S(hip=(52, 53), t=90, hand=('rel', 1, 26), es=1, foot=(52, 89), ks=-1, ft=-15), B=S(hip=(52, 47), t=90, hand=('rel', 1, 26), es=1, foot=(53, 84), ks=-1, ft=-60)),
 'crunch': S(eq='none', A=S(hip=(58, 88), t=178, hn=0, hand=('rel', -3, -6), es=1, foot=(78, FLOOR), ks=1), B=S(hip=(58, 88), t=146, hand=('rel', -3, -6), es=1, foot=(78, FLOOR), ks=1)),
 'plank': S(eq='none', A=S(hip=(60, 80), t=176, hand=(44, FLOOR), es=-1, foot=(92, FLOOR), ks=1, ft=-60), B=S(hip=(60, 76), t=174, hand=(44, FLOOR), es=-1, foot=(92, FLOOR), ks=1, ft=-60)),
 'hyper': S(eq='none', mach=['M44 64L60 68', 'M52 66V94'], A=S(hip=(52, 60), t=-62, hand=('rel', 3, 8), es=1, foot=(18, 76), ks=1), B=S(hip=(52, 60), t=4, hand=('rel', -6, 6), es=1, foot=(18, 76), ks=1)),
}

if __name__ == '__main__':
    out = {k: svg(v) for k, v in FIGS.items()}
    js = 'const FIG = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';'
    p = pathlib.Path(__file__).resolve().parent.parent / 'index.html'
    s = p.read_text()
    a, b = '/* FIGURES:BEGIN (generiert von tools/figures.py) */', '/* FIGURES:END */'
    if a in s:
        s = s[:s.index(a) + len(a)] + '\n' + js + '\n' + s[s.index(b):]
        p.write_text(s)
    pathlib.Path('/tmp/claude-0/-home-user/0e712108-d47d-506b-8394-a74143171eb0/scratchpad/figs.json').write_text(json.dumps(out))
    print(len(out), 'Figuren,', len(js) // 1024, 'KB')
