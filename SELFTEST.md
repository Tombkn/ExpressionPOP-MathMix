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

Erneut TouchDesigner 2025.33230 (v1.9.1, 2026-10-01): dieselbe Zeile, größte
Abweichung **0.0**. *Re-run on 2025.33230: max deviation 0.0.*

## Mehrere Eingänge / Several inputs (1.8)

**Idee:** Denselben POP in **beide** Eingänge hängen. Dann muss `in1_P` Punkt für
Punkt dasselbe sein wie `P`, und die Differenz ist überall 0.

*Feed the same POP into both inputs: `in1_P` must then equal `P` point for point.*

### So testest du / How to run

1. Seite **Inputs**, "+" drücken. Der Node bekommt einen zweiten Stecker.
2. **Denselben** POP in beide Stecker hängen (z. B. einen Point Generator POP).
3. Auf der Inputs-Seite steht jetzt in beiden Blöcken dieselbe Attributliste,
   nur mit unterschiedlichem Präfix:
   `P[vec3], Age[float]` und `in1_P[vec3], in1_Age[float]`.
4. Eine OutAttr-Zeile:

```
selftest2 = length(P - in1_P) + abs(float(_NumPoints) - float(_NumPoints))
```

Muss auf jedem Punkt **0.0** sein.

**Gegenprobe, damit der Test etwas beweist:** einen *anderen* POP in den zweiten
Stecker hängen. Jetzt muss der Wert **ungleich 0** sein. Ohne diesen Schritt
könnte die Zeile auch dann 0 zeigen, wenn `in1_P` gar nichts liest.

*Control: wire a different POP into the second input; the value must now be
non-zero. Without that step a passing test proves nothing.*

### Was dabei mitbewiesen wird / Also covered

| Beobachtung | Was sie zeigt |
|---|---|
| Zeile kompiliert | `in1_` wird als Präfix erkannt und zu `TDIn_P(1u, _id1)` übersetzt |
| Ergebnis 0.0 | der zweite Eingang wird punktgenau gelesen, kein Indexversatz |
| Gegenprobe ≠ 0 | es wird wirklich Eingang 2 gelesen, nicht zweimal Eingang 1 |
| `_NumPoints`-Term 0.0 | Built-ins beziehen sich weiter auf den **ersten** Eingang |
| **Use As** zeigt beide Listen | die Anzeige folgt dem, was wirklich am Stecker hängt |

### Length Mismatch prüfen / Checking Length Mismatch

Den zweiten Point Generator POP auf **3** Punkte stellen, den ersten auf 10, und
`cp = in1_P` schreiben. Dann zeigt `cp`:

| Length Mismatch | ab Punkt 3 |
|---|---|
| Repeat | die drei Positionen im Kreis, `id % 3` |
| Hold | immer die letzte, Punkt 2 |
| Zero | Nullen |
| One | Einsen |

Auf **1** Punkt gestellt liest jeder Punkt denselben Wert, in jedem Modus, weil
ein Einzelpunkt-Eingang eine Konstante ist.

### Leerer Stecker / Empty connector

Einen Block mit "+" anlegen und **nichts** anschließen. Der Node muss weiter
laufen: der Eingang liest dann einen 1-Punkt-Ersatz, `in1_P` ist `0.0`. Ein
Attributname, den es dort nicht gibt, sagt weiterhin klar
`'in1_Heat' : undeclared identifier`.

### Verifiziert / Verified

TouchDesigner 2025.32820, Noise POP mit 3050 Punkten in beide Stecker: Abweichung
**0.0** auf allen 3050 Punkten. Gegenprobe mit einem anderen POP am zweiten
Stecker: Maximum **9.85**, der Test schlägt also an.
