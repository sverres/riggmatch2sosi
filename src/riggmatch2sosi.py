# -*- coding: utf-8 -*-
# riggmatch2sosi.py
#
# Leser inn og matcher data fra to filer:
# Data fra borerigg med info om boredybde kobles sammen med
# innmålte posisjoner i KOF-fil.
# Resultatet skrives ut på SOSI-format.
#
# Made by: sverre.stikbakke@hig.no 11.11.11
#
# Oppdatert til python 3 25.03.19
#
# =============================================================================

# Datafiler inn
riggrapport = "KS_PEL_1.csv"
posisjoner = "KS_Pel_1_Test_Sosi.kof"
sosihode = "sosihode.txt"

# SOSI-fil ut
sosifil = "KS_PEL_1.SOS"

# Faste parametre som skrives til fil
KVALITET = "11 1"

# Faste parametre som brukes i beregningene
delta_z = 0.5  # Avstand målepunkt på rigg til bakkenivå

# =============================================================================

# Leser inn riggdata

Rigg_data = {}  # Python dictionary

with open(riggrapport) as rigg_file:
    for pel in rigg_file.readlines():
        # Tilordner verdier fra datafil til variabler
        # Verdiene skilles fra hverandre med ";"
        (Column_name,
         Date,
         Time,
         Depth_m,
         Stabilized_m,
         M_pluss,
         M_minus,
         Avg_kg_ls,
         Start_weight,
         Drill_time_s,
         Stab_s,
         Elev_mm_r,
         Tank_no,
         Orginal_name,
         Dummy,
         Dummy,
         Dummy) = pel.split(";")

        # Lagrer aktuelle data om hver pel
        Rigg_data[Column_name] = (
            Column_name,
            Date,
            Time,
            Depth_m)


# Leser inn koordinatfil

Pos_data = {}   # Python dictionary

x_min = 999999.0
x_max = 0.0
y_min = 9999999.0
y_max = 0.0

with open(posisjoner) as pos_file:
    for pel in pos_file.readlines():
        if pel.startswith(" 05"):
            # Tilordner verdier fra datafil til variabler
            # Verdiene skilles fra hverandre med "whitespace"
            (Dummy,
             Id,
             Nord,
             Ost,
             Hoyde_XYZ0) = pel.split()

            # Lagrer aktuelle data om hver pel
            Pos_data[Id] = (
                Id,
                Ost,
                Nord,
                Hoyde_XYZ0)

            # Finner områdets utstrekning
            if float(Ost) < x_min:
                x_min = float(Ost)

            if float(Ost) > x_max:
                x_max = float(Ost)

            if float(Nord) < y_min:
                y_min = float(Nord)

            if float(Nord) > y_max:
                y_max = float(Nord)


# Leser inn fil med SOSI-hode

with open(sosihode, encoding='utf-8') as sosi_hode_file:
    hode = sosi_hode_file.read()


# Matcher data fra de to filene basert på "Column_name" og "Id" som er
# nøkler i dictionariene Rigg_data og Pos_data.

with open(sosifil, "w", encoding='utf-8') as sosi_file:
    sosi_file.write(hode)

    kurvenr = 0

    for pel in Rigg_data:
        if Pos_data.get(pel):
            # Henter ut verdier fra Pos_data
            pel_data_pos = Pos_data.get(pel)

            pel_ID = pel_data_pos[0]
            x = float(pel_data_pos[1])
            y = float(pel_data_pos[2])
            z2 = float(pel_data_pos[3])  # innmålt høyde topp av pel

            # Henter ut verdier fra Rigg_data
            pel_data_rigg = Rigg_data.get(pel)

            boredybde_rigg = pel_data_rigg[3].replace(",", ".")
            boredybde = float(boredybde_rigg) - delta_z

            # Beregne bunnen av borehull
            z1 = z2 - boredybde

            # Omformer variabler til tekst-variabler uten desimaler
            kurvenr = kurvenr + 1  # Løpenummer i SOSI-fil
            KURVE = str(kurvenr)

            BORLENGDE = str(round(boredybde * 1000, 0))[0:-2]  # Boredybde i mm

            (dag,
             mnd,
             aar) = pel_data_rigg[1].split(".")
            DATAFANGSTDATO = aar + mnd + dag

            N = str(y * 1000)[0:-2]
            E = str(x * 1000)[0:-2]
            H1 = str(round(z1 * 1000, 0))[0:-2]
            H2 = str(round(z2 * 1000, 0))[0:-2]

            sosi_objekt = (
                f".KURVE {KURVE}:\n"
                f"..OBJTYPE GeofLinjeInfo\n"
                f"..ID {pel_ID}\n"
                f"..DATAFANGSTDATO {DATAFANGSTDATO}\n"  # Fra riggrapport
                f"..BORLENGDE {BORLENGDE}\n"
                f"..KVALITET {KVALITET}\n"  # Fast verdi for alle objekter
                f"..NØH\n"
                f"{N} {E} {H1}\n"
                f"{N} {E} {H2}")

            print(sosi_objekt, file=sosi_file)
    print(".SLUTT", file=sosi_file)

print
print("Data for "
      + str(kurvenr)
      + " peler skrevet til SOSI-fil.")
print()
print("Avgrensning: ",
      round(y_min, 0),
      round(x_min, 0),
      round(y_max, 0),
      round(x_max, 0))
print()
input("OK?")
