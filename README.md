# vektis-python

Python routines om Vektis-bestanden aan te maken en in te lezen.

## Dependencies
vektis-python gebruikt xlrd om Vektis definitiebestanden in te lezen.

## Gebruik
Lees een spreadsheat met de Vektis-definitie in:

```python
vektis_def = vektis.VektisDefinitie("ZH308", "9.0")
vektis_def.laad_specificatie()
```

laad_specificatie() zoekt naar een definitiebestand in dezelfde map als het bronbestand. Het verwacht
dat het definitiebestand begint met &lt;standaard&gt;v&lt;versie&gt; heeft. In bovenstaand voorbeeld 
moet het bestand dus beginnen met ZH308v9.0.

Je kunt hiervan afwijken door een configuratie-object mee te geven aan de constructor
van *VektisDefinitie*.

```python
vektis_def = vektis.VektisDefinitie("ZH308", "9.0", 
    vektis.Config(map="c:\\vektis\\definities"))
```

De Config klasse heeft de volgende keyword parameters:
* **map** - map waar het Vektis-definitiebestand voor deze standaard staat;
* **regexp** - reguliere expressie waaraan de naam van het definitiebestand aan moet voldoen 
    (standaard "&lt;STANDAARD&gt;v&lt;VERSIE&gt;.+", waarbij &lt;STANDAARD&gt; en &lt;VERSIE&gt; worden vervangen
    door de werkelijke standaard en versie);
* **sheet** - het nummer van de sheet, beginnend bij 0 (standaard 1);
* **startrow** - het rijnummer waar moet worden begonnen met inlezen, beginnend bij 0 (standaard 11).

Vervolgens instantieer je een *VektisInstantie* object:

```python
vektis_inst = vektis.VektisInstantie(zh308_def)

```

*vektis_inst* gebruik je om het Vektisbestand op te bouwen.

Stel de Vektisstandaard is ZH308 en je hebt een verzameling declaraties om in te dienen:

```python
vektis_inst.nieuw_record("VOORLOOPRECORD", data=Voorlooprecord(nota))

for declaratie in nota.declaraties:
        vektis_inst.nieuw_record("VERZEKERDENRECORD", data=Verzekerdenrecord(declaratie))
        vektis_inst.nieuw_record("PRESTATIERECORD", data=Prestatierecord(declaratie))
        vektis_inst.nieuw_record("TARIEFRECORD", data=Tariefrecord(declaratie))
        
        for zorgactiviteit in declaratie.zorgactiviteiten:
            vektis_inst.nieuw_record("ZORGACTIVITEITRECORD", data=Zorgactiviteitrecord(zorgactiviteit))
            
vektis_inst.nieuw_record("SLUITRECORD", data=Sluitrecord(nota))
```

Parameter 'data' is een instantie van een klasse die is afgeleid van *vektis.VektisData*. 
De constructor van VektisData verwacht een enkel item. Dit kan van alles zijn, bijvoorbeeld een record
uit een database.

Parameter 'data' is optioneel. Als 'data' niet wordt opgegeven, dan probeert nieuw_record() het object
te gebruiken dat is meegegeven aan de constructor van VektisInstantie. Als dat er ook niet is,
dan volgt een GeenDataException.

Nadat alle records zijn toegevoegd is str(vektis_inst) het vektisbestand dat kan worden ingediend.

