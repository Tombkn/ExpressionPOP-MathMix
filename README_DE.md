# Expression POP + Math Mix

Schreib Math-Mix-Operationen direkt in eine Expression-Zeile, mit denselben Namen
und Formeln wie im **Math Mix POP**-Menü:

```
Color = Color * ifelse(1.0, 0.2, gt(Age, 30.0))
P.y   = zigzag(_PointCy * 4.0, -1.0, 1.0)
heat  = remap(Age, 0.0, 60.0, 0.0, 1.0)
```

Das ist der Expression POP von **Function Store** ([das ExpressionPOP-Video](https://www.youtube.com/watch?v=fQco5ADaHyw))
mit eingebauter GLSL-Funktionsbibliothek. Ein normaler Expression POP kennt nur
pures GLSL und antwortet auf `rangefrom` mit *„no matching overloaded function found"*.

Nichts zu installieren, nichts einzustellen. Reinziehen und lostippen.

---

## Los geht's

1. **`ExpressionPOP_MathMix.tox`** ins Netzwerk ziehen.
2. Einen POP an den Eingang hängen.
3. Auf der Parameterseite neben *Expr* auf "+" drücken und eine Zeile schreiben.
4. Ergebnis anschauen: Mittelklick auf den Node, oder einen Null POP dahinter.

Mehr ist es nicht. Projekt speichern wie immer.

---

## Was du schreiben kannst

### Attribute, die es schon gibt

Alles, was dein Eingang mitbringt (`P`, `N`, `Color`, `Age` …), kannst du lesen
und schreiben:

```
P = P * 1.5
Color = Color * 0.5
```

### Neue Attribute, einfach hinschreiben

Schreib links einen Namen, den der Eingang nicht hat, und er wird angelegt:

```
heat  = _PointU * 5.0             neues Attribut, 1 Wert pro Punkt
shift = vec3(_PointU, 1.0, 2.0)   neues Attribut, 3 Werte pro Punkt
```

Die Breite ergibt sich aus dem, was rechts steht: ein `vec2/3/4(…)` gibt 2/3/4
Werte, alles andere gibt 1.

Steht rechts kein `vec2/3/4(…)`, sind es aber trotzdem mehrere Werte, etwa
`P - _BoundsCenterP`, schreib den Typ vor den Namen, genau wie bei einer Local-Zeile:

```
vec3 offset = P - _BoundsCenterP   neues Attribut, 3 Werte pro Punkt
```

Einzelne Komponenten gehen auch: `P.y = 0.0`, `Color.a = 0.5`.

### Built-ins: jeder `_`-Name ist sofort nutzbar

Du musst dafür nichts vorbereiten. Die gibt es in jeder Expression:

| Built-in | Was du bekommst | Bei 10 Punkten |
|---|---|---|
| `_PointI` | Nummer dieses Punkts, ab 0 | `0 … 9` |
| `_PointU` | Position entlang der Punkte, 0 bis 1 | `0 … 1` |
| `_PointCy` | dasselbe, erreicht die 1 aber nie (zyklisch) | `0 … 0.9` |
| `_NumPoints` | wie viele Punkte es gibt | `10` |
| `_NumPrims` · `_NumVerts` | dasselbe für Primitives / Vertices | `10` |
| `_VertI` · `_PrimI` | Nummer innerhalb Vertices / Primitives | `0 … 9` |
| `_VertU` `_VertCy` `_PrimU` `_PrimCy` | die 0-bis-1-Varianten davon | `0 … 1` |
| `_VertPrimI` · `_VertPrimU` · `_NumVertsPrim` | Position eines Vertex in seinem Primitive | braucht Primitives |
| `_DimI[0]` | Gitterkoordinate entlang Achse 0 | `0 … 9` |
| `_DimSize[0]` · `_DimU[0]` · `_DimCy[0]` | Größe / 0-bis-1 / zyklisch dieser Achse | `10` · `0…1` · `0…0.9` |
| `_NumDim` | Anzahl der Dimensionen | `1` |
| `_BoundsMinP` · `_BoundsMaxP` · `_BoundsCenterP` | Bounding Box des Eingangs, als vec3 | live gemessen |
| `_StepSeconds` | ein Frame in Sekunden | `0.01667` bei 60 fps |
| `_StepFrames` | ein Frame | `1` |
| `_Pi` | 3.14159… | `3.142` |
| `_MaxInt` · `_MaxUInt` · `_NoNeighbor` | die üblichen Grenzwert-Konstanten | |

Nur `_ArrayI` / `_ArrayU` / `_ArrayCy` fehlen, denn die zählen innerhalb einer
Array-Operation, wofür eine Zeile pro Punkt kein Gegenstück hat.

**Alles in einer Zeile ist für jeden Punkt gleich, außer den Built-ins.**
Sie sind die einzige Stelle, an der ein Punkt weiß, dass er nicht Punkt 0 ist.

### Math-Mix-Funktionen

| In Math Mix | Hier | Anmerkung |
|---|---|---|
| Namen, die GLSL schon hat: `abs sign sqrt floor round ceil fract normalize exp exp2 log2 sin cos tan asin acos atan degrees radians length min max mod dot cross reflect refract mix clamp smoothstep` | gleicher Name | GLSL-Semantik, Trigonometrie in **Radiant**. Für Grad: `sind cosd tand asind acosd atand` |
| `A ** B` | `pow(A, B)` | |
| `1 / A` | `inv(A)` | `inverse` ist in GLSL die Matrix-Inverse, daher der andere Name. A = 0 bleibt 0 |
| `int(A)` · `int(A / B)` | `trunc(A)` · `intdiv(A, B)` | |
| `A if C else B` | `ifelse(A, B, C)` | **Bedingung kommt zuletzt.** `ifelse(7, 3, gt(u, 0.5))` ergibt 7, wenn u > 0.5 |
| `A > B` … `A != B` | `gt gte lt lte eq ne` | liefern 1.0 oder 0.0 · `eqtol(A, B, tol)` für Floats |
| `B <= A < C` und Verwandte | `bltealtc bltaltec bltaltc bltealtec` | |
| `rangefrom rangeto loop zigzag mix clamp smoothstep` | gleiche Namen | zusätzlich `remap(A, from1, from2, to1, to2)` |
| `logB avg exp10 log10 ln square` | gleiche Namen | `ln` und `log10` geben A unverändert zurück für A ≤ 0 |
| `compadd compsub compmult compdiv compavg compmin compmax` | gleiche Namen | für float, vec2, vec3, vec4. `compdiv` liefert 0 bei Division durch 0, wie Math Mix |
| `arraylength arrayadd arraymult arrayavg arraymin arraymax` | gleiche Namen | für Float-Array-Attribute |
| `atan2(A, B)` · `angle(A, B)` | gleiche Namen, in **Grad** | Radiant-Zwillinge: `atan2rad` `anglerad` |
| `dbtopow powtodb dbtoamp amptodb` | gleiche Namen | |
| `RGBtoHSV` · `HSVtoRGB` | gleiche Namen | vec3 und vec4 |

### Werte von außen

Eine Zahl, die aus einem Parameter oder CHOP kommen soll, geht als Uniform rein:
in die Komponente gehen (`i`), `glsl1` anwählen, Seite *Vectors*, einen Vektor
namens `uAmp` anlegen (Typ `float`, Wert oder Expression). Dann `heat = _PointU * uAmp`
schreiben. Der Wert ändert sich jeden Frame, ohne dass der Shader neu kompiliert.

---

## OutAttr / Local

Jede Zeile hat einen Schalter. Lass ihn **aus**, außer du brauchst einen
Zwischenwert.

| Schalter | Wofür |
|---|---|
| **OutAttr** (aus) | ein Attribut schreiben, der Normalfall |
| **Local** (an) | ein Wert, den die Zeilen darunter weiterverwenden |

Local ist ein Schmierzettel: du rechnest etwas aus, benutzt es zweimal, und
wirfst es weg. Es wird nie ein Attribut.

```
[Local]    float d = length(P)
[OutAttr]  P     = P * (1.0 + d * 0.1)
[OutAttr]  Color = vec4(d, d, d, 1.0)
```

`length(P)` wird **einmal** gerechnet und zweimal benutzt, und es gibt nur eine
Stelle, an der du es später änderst.

**Eine Local-Zeile braucht ihren Typ links.** Das ist die eine Regel, die man
sich merken muss:

| Modus | Du schreibst | Ergebnis |
|---|---|---|
| OutAttr | `cool = vec4(3)` | läuft: Attribut `cool` = `[3,3,3,3]` |
| Local | `cool = vec4(3)` | scheitert: `'cool' : undeclared identifier` |
| Local | `vec4 cool = vec4(3)` | läuft |

Warum: Im OutAttr-Modus **ist** `cool` das Attribut, und um seinen Typ kümmert
sich die Komponente. Im Local-Modus ist `cool` eine ganz normale Variable im
Shader, und die brauchen einen Typ, wie in C.

Außerdem: Local-Zeilen müssen **über** den Zeilen stehen, die sie benutzen.

---

## Wenn etwas nicht geht

| Meldung / Symptom | Ursache | Abhilfe |
|---|---|---|
| `'name' : undeclared identifier`, obwohl der Name eine Zeile höher steht | diese Zeile ist *Local*, hat aber keinen Typ | `vec4 cool = vec4(3)` statt `cool = vec4(3)` schreiben |
| `cannot convert` / `no matching operator` zwischen eigenen Werten | unterschiedliche Breiten, z. B. `cool + vec3(1)` bei `vec4 cool` | angleichen: `cool + vec4(1)` |
| `cannot convert from 'vec3' to 'float'` bei einem **neuen** Attribut | die Breite wurde aus der rechten Seite geraten, und dort steht kein `vec3(…)` | Typ vor den Namen: `vec3 offset = P - _BoundsCenterP` |
| `undeclared identifier` bei einem Attribut, das es geben sollte | Tippfehler, oder kein **Point**-Attribut des **ersten** Eingangs | Mittelklick auf den Eingang zeigt seine Attribute |
| ein Vergleich liefert 0 oder 1 statt deiner zwei Werte | Argumentreihenfolge von `ifelse` | Bedingung zuletzt: `ifelse(A, B, C)` heißt *A wenn C, sonst B* |
| ein Wert ist 0, obwohl er es nicht sein dürfte | Ganzzahl-Division, denn `1 / 2` ist in GLSL 0 | `1.0 / 2.0` schreiben. Ganze Zahlen als Argumente sind okay: `remap(Age, 0, 60, 0, 1)` läuft |
| alles kompiliert, aber unten ändert sich nichts | die Zeile steht auf *Local* | auf *OutAttr* stellen, oder den lokalen Wert in einer *OutAttr*-Zeile darunter verwenden |
| die Meldung passt nicht zu dem, was du gerade getippt hast | das *Info*-Feld kann einen Cook hinterherhinken | Expression antippen für einen neuen Cook, dann nochmal lesen |

Stell **View** auf *info* für Compile-Meldungen und auf *code* für den Shader,
den deine Zeilen erzeugen. Die Zeilennummern in Fehlern passen zu dem, was
*code* zeigt.
