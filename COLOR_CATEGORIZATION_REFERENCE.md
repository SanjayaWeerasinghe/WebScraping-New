# Color Categorization Reference

This document provides a complete mapping of specific color shades to their main color categories used in the Fashion Scraper Dashboard.

## Overview

The system categorizes **254+ unique color names** from scraped products into **12 main color categories** for easier analysis and visualization.

---

## Main Color Categories

### 1. BLACK
**Main Category Color:** `#000000`

**Included Shades:**
- black
- ebony
- onyx
- jet
- noir
- charcoal
- eerie
- raisin
- smoky

**Note:** Black is checked first to avoid false matches with compound colors like "blue-black"

---

### 2. WHITE
**Main Category Color:** `#FFFFFF` (displayed as `#9CA3AF` in some charts for visibility)

**Included Shades:**
- white
- ivory
- cream
- alabaster
- pearl
- cultured
- magnolia
- vanilla
- bone
- isabelline
- ghost

---

### 3. GRAY
**Main Category Color:** `#6B7280`

**Included Shades:**
- gray / grey
- silver
- slate
- ash
- dim gray
- gunmetal
- nickel
- platinum
- gainsboro
- manatee
- quick silver
- sonic silver
- roman silver
- davy
- payne
- feldgrau
- cadet grey
- spanish gray
- granite
- cinereous
- grullo

---

### 4. RED
**Main Category Color:** `#DC2626`

**Included Shades:**
- red
- maroon
- crimson
- scarlet
- burgundy
- wine
- cardinal
- carmine
- claret
- ruby
- brick
- cordovan
- vermillion
- madder
- upsdell

---

### 5. BLUE
**Main Category Color:** `#2563EB`

**Included Shades:**
- blue
- navy
- azure
- cobalt
- sapphire
- indigo
- cerulean
- periwinkle
- cornflower
- teal
- prussian
- denim
- han blue
- yinmn
- oxford
- cadet blue
- alice
- space cadet
- queen blue
- morning blue
- powder blue

---

### 6. GREEN
**Main Category Color:** `#16A34A`

**Included Shades:**
- green
- olive
- lime
- emerald
- mint
- sage
- jungle
- viridian
- shamrock
- hooker
- phthalo
- kombu
- castleton
- rifle
- pine
- sacramento
- msu green
- russian green
- english green
- artichoke
- laurel
- charleston
- zomp

---

### 7. YELLOW
**Main Category Color:** `#FACC15`

**Included Shades:**
- yellow
- gold
- mustard
- amber
- lemon
- jonquil
- maize
- hansa
- earth yellow
- harvest
- sunray

---

### 8. ORANGE
**Main Category Color:** `#F97316`

**Included Shades:**
- orange
- coral
- peach
- tangerine
- apricot
- melon
- persian orange
- copper

---

### 9. PURPLE
**Main Category Color:** `#9333EA`

**Included Shades:**
- purple
- violet
- lavender
- mauve
- plum
- lilac
- eggplant
- byzantium
- grape
- mulberry
- thistle
- languid
- cyber grape
- independence
- prune
- puce

---

### 10. PINK
**Main Category Color:** `#EC4899`

**Included Shades:**
- pink
- rose
- fuchsia
- magenta
- blush
- cameo
- charm
- champagne
- cyclamen
- mountbatten
- nadeshiko
- pastel
- queen pink
- raspberry
- sherbet
- tango pink
- quinacridone
- shimmering

---

### 11. BROWN
**Main Category Color:** `#92400E`

**Included Shades:**
- brown
- tan
- beige
- khaki
- taupe
- camel
- chocolate
- coffee
- sienna
- umber
- sepia
- bistre
- bronze
- brass
- burnished
- liver
- beaver
- bole
- brandy
- buff
- burnt
- café
- caput
- chestnut
- coyote
- fawn
- kobicha
- sand
- tumbleweed
- tuscan
- wood
- van dyke
- redwood
- opal
- desert
- almond
- auburn
- deer

---

### 12. MULTICOLOR
**Main Category Color:** Linear gradient (multiple colors)

**Included Keywords:**
- multi
- print
- pattern
- mix
- assorted

**Note:** Used for items that have multiple colors or patterns

---

### 13. OTHER
**Main Category Color:** `#A8A29E`

**Description:** Catch-all category for any color that doesn't match the above categories

**Examples:**
- Uncommon or unique color names
- Misspellings
- Colors not fitting standard categories

---

## Usage in System

### Frontend (ColorTrends.tsx)
The `categorizeColor()` function processes each product's color and returns the appropriate main category. This is used for:
- Color Price Evolution chart (tracking price trends by color)
- Most Used Colors pie chart
- Color distribution analysis

### Backend (api.py)
The same categorization logic is implemented in the `/api/color-price-trends` endpoint to:
- Aggregate pricing data by color category
- Calculate average prices per color over time
- Support filtering by site and gender

### Special Cases

**FashionBug Tops:**
For FashionBug products that are tops (T-Shirt, Shirt, Blouse, Top), the system uses the **2nd color** if available, as the 1st color might be from pants in the product photo.

**CoolPlanet & Other Items:**
All other products use the **1st color** from their color array.

---

## Statistics

- **Total Main Categories:** 12 + Other
- **Total Unique Colors in Database:** 254+
- **Most Common Categories:** Black, Blue, White, Red
- **Products Tracked:** 1,220+
- **Time Range:** 30 days of historical data

---

## Maintenance

When adding new color mappings:
1. Identify which main category the new shade belongs to
2. Add the lowercase keyword to the appropriate category in `categorizeColor()`
3. Update this reference document
4. Test with sample data to ensure correct categorization

---

**Last Updated:** 2025-10-18
**Version:** 1.0
