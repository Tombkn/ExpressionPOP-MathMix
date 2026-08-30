# Selbsttest / Self-test: eine Expression, die 0 ergeben muss

**Idee:** Jede Komponente vergleicht Funktionen gegen ihre bekannte Formel und
gibt die Abweichung zurück. **Alles 0 = alles korrekt.** Du musst keine
Zahlenkolonnen prüfen, nur schauen, ob irgendwo etwas ≠ 0 steht.

*Each component compares functions against their known formula and returns the
deviation. **All zeros = everything works.***

## So testest du / How to run

1. Einen POP an den Eingang hängen, z. B. einen Point Generator POP mit 10 Punkten.
2. Neben *Expr* auf "+" drücken, **OutAttr/Local** auf **aus** lassen.
3. Die Zeile unten komplett hineinkopieren, sie ist **eine** Zeile.
4. Ergebnis anschauen (Mittelklick auf den Node oder ein Null POP dahinter):
   das Attribut `selftest` muss in allen vier Komponenten **0.0** sein.

Ist eine Komponente ≠ 0, sagt sie dir gleich die Gruppe (siehe Tabelle unten).

## Die Expression / The expression

```
selftest = vec4(abs(remap(_PointU,0.0,1.0,10.0,20.0)-(10.0+10.0*_PointU))+abs(rangeto(_PointU,0.0,4.0)-4.0*_PointU)+abs(rangefrom(_PointU,0.0,2.0)-_PointU*0.5)+abs(loop(_PointU*3.0,0.0,1.0)-fract(_PointU*3.0)), abs(ifelse(7.0,3.0,gt(_PointU,0.5))-(_PointU>0.5?7.0:3.0))+abs(lt(_PointU,0.5)-float(_PointU<0.5))+abs(float(_PointU>=0.0)-1.0)+abs(ne(_PointU,_PointU)-0.0), abs(compadd(vec3(1.0,2.0,3.0))-6.0)+abs(compavg(vec3(3.0,6.0,9.0))-6.0)+abs(compmax(vec3(1.0,5.0,2.0))-5.0)+abs(compmin(vec3(1.0,5.0,2.0))-1.0), abs(sind(90.0)-1.0)+abs(cosd(0.0)-1.0)+abs(amptodb(1.0))+abs(square(3.0)-9.0)+abs(inv(4.0)-0.25)+abs(avg(2.0,8.0)-5.0))
```

## Was jede Komponente prüft / What each component covers

| Komponente | Geprüft | Gegen welche Formel |
|---|---|---|
| **x** | `remap` `rangeto` `rangefrom` `loop` + Built-in `_PointU` | `remap(u,0,1,10,20)` = `10+10u` · `rangeto(u,0,4)` = `4u` · `rangefrom(u,0,2)` = `u/2` · `loop(u·3,0,1)` = `fract(u·3)` |
| **y** | `ifelse` `gt` `lt` `ne` und Vergleiche mit `>=` in derselben Zeile | `ifelse(A,B,C)` = *A wenn C, sonst B* · Vergleichsfunktionen geben 1.0/0.0 |
| **z** | `compadd` `compavg` `compmax` `compmin` | `1+2+3` = 6 · `(3+6+9)/3` = 6 · `max` = 5 · `min` = 1 |
| **w** | `sind` `cosd` `amptodb` `square` `inv` `avg` | `sin(90°)` = 1 · `cos(0°)` = 1 · `20·log₁₀(1)` = 0 · `3²` = 9 · `1/4` = 0.25 · `(2+8)/2` = 5 |

Nebenbei bewiesen, ohne dass du etwas tun musst:

- **Neue Attribute entstehen automatisch**, `selftest` gibt es auf keinem
  Eingang, es taucht trotzdem hinter dem Node auf.
- **Die Breite stimmt**, `vec4(…)` ergibt vier Komponenten. Wäre das falsch,
  bekämest du einen Typfehler statt eines Ergebnisses.
- **Fehlerzeilen passen**, bau absichtlich einen Tippfehler ein (`sindd(90.0)`);
  die Zeilennummer unter **View = info** zeigt auf die Zeile, die **View = code**
  anzeigt.

## Was der Test NICHT abdeckt / Not covered

- **Array-Funktionen** (`arrayadd` & Co.), dafür braucht der Eingang ein
  Float-Array-Attribut, das eine Expression allein nicht herstellt. Prüfen mit
  einem Attribute POP, der z. B. `Weights[4]` anlegt, dann
  `float s = arrayadd(Weights)`.
- **`_BoundsMinP` / `_BoundsMaxP` / `_BoundsCenterP`**, hängen vom Eingang ab,
  ein fester Erwartungswert lässt sich nicht in die Zeile schreiben.
- **Vertex- und Primitive-Built-ins** (`_VertPrimI`, `_NumVertsPrim`), brauchen
  Geometrie mit Primitives statt reiner Punkte.
- **`RGBtoHSV` / `HSVtoRGB`**, ließen sich als Rundreise prüfen
  (`RGBtoHSV(HSVtoRGB(x)) − x`), macht die Zeile aber deutlich länger.

## Verifiziert / Verified

TouchDesigner 2025.32820, Point Generator POP mit 10 Punkten: alle vier
Komponenten **0.0** an jedem Punkt, größte Abweichung über alle Punkte **0.0**,
keine Compile-Fehler.
