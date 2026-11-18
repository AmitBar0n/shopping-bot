# RoomFit 3D – real-size room & furniture planner

A single-file web app (`index.html`). It needs no build step and no server code: open it in a browser or upload it to any website.

## What the visitor can do

1. **Start a room** in one of two ways:
   - **Room by dimensions:** type the inside width, length and ceiling height. Then mark doors and windows: select a wall and click **+ Door** / **+ Window**, and type the exact distance from the wall's start or end. You can also click a wall with the Door / Window tool.
   - **Upload a floor plan** (JPG, PNG or PDF):
     1. **Set scale:** click both ends of a distance you know and type the real length.
     2. **Auto-detect walls**, which finds thick dark lines in the image. Or trace the walls with the Wall tool: corners snap together, and you can type a length and press Enter.
     3. **Place doors and windows:** click on a wall, or into a gap in the plan.
2. **Furnish:** add items from the catalogue, or import your own `.glb` model. The catalogue handles hundreds of items: you can search by name, code or tag, filter by category, and see thumbnails and prices. Every item is real size, and you can edit its width, depth, height, height above the floor and rotation.
3. **Check the fit:**
   - Items that hit a wall, a door swing or other furniture get a red outline.
   - The plan shows the free space from the selected item to the nearest wall in each direction.
4. **View:** 2D plan, 3D view, or both side by side. In 3D you can orbit, look from the top, or **walk** through the room at 160 cm eye height. In cutaway mode, walls between the camera and the room become see-through.
5. **Save:**
   - Work is autosaved in the browser.
   - **Save file** / **Open file** downloads the project as a `.json` file and opens it again.
   - **Image** downloads a PNG of the current view.

Units: centimetres or inches (switch in Settings).

## Keyboard

| Key | Action |
|---|---|
| R / Q / E | rotate 90° / −15° / +15° |
| Arrows (Shift) | nudge 1 cm (10 cm) |
| Del | delete selection |
| Ctrl+Z / Ctrl+Y | undo / redo |
| Ctrl+D | duplicate |
| V W M D N | Select, Wall, Measure, Door, Window tool |
| Esc | finish wall / cancel tool |
| W A S D | walk (in Walk mode) |

## Putting it on a website

Upload `index.html` and either link to it or embed it:

```html
<iframe src="/room-planner/index.html" style="width:100%;height:85vh;border:0" allow="fullscreen"></iframe>
```

### Optional configuration (own products, branding)

Add this **before** the module script in `index.html`. There is a placeholder `<script>` block for it.

```html
<script>
window.ROOMFIT_CONFIG = {
  title: 'My Furniture Store – Room Planner',
  accent: '#0a7d5a',            // brand colour
  units: 'cm',                  // or 'in'
  hideDefaultCatalog: false,    // true = show only your products
  products: [
    // sizes in cm. "model" is a .glb file. It is scaled to exactly w × d × h.
    { id: 'oslo-sofa', name: 'Oslo sofa', category: 'Our sofas', w: 230, d: 98, h: 82, model: '/models/oslo-sofa.glb' },
    // no model? use a built-in shape: sofa, bed, table, roundtable, chair, desk, wardrobe,
    // bookshelf, dresser, tvstand, tv, fridge, counter, washer, bathtub, rug, plant, lamp, box
    { id: 'nordic-table', name: 'Nordic table', category: 'Our tables', type: 'table', w: 200, d: 95, h: 75, color: '#9c7b58' },
  ],
};
</script>
```

### Large catalogue (hundreds of items): use a catalogue file

Keep the products in a spreadsheet, export it as **CSV** (or write JSON), upload it next to `index.html`, and point the config at it:

```html
<script>
window.ROOMFIT_CONFIG = { catalogUrl: 'catalog.csv', currency: 'ILS', hideDefaultCatalog: true };
</script>
```

There's a template in `catalog.example.csv`. Columns:

| Column | Required | Meaning |
|---|---|---|
| `id` | yes | Unique code, used in `?add=` links |
| `name` | yes | Shown in the list |
| `category` | yes | Groups the list and the category filter |
| `w`, `d`, `h` | yes | Real size in **cm** (width, depth, height) |
| `model` | – | `.glb` file. Draco or Meshopt compressed is fine and recommended. It is scaled to exactly w × d × h |
| `type` | – | Built-in shape if there's no model: `sofa bed table roundtable chair desk wardrobe bookshelf dresser tvstand tv fridge counter washer bathtub rug plant lamp box` |
| `color` | – | Hex colour for built-in shapes |
| `elev` | – | Height above the floor in cm (e.g. a wall shelf or a TV) |
| `price` | – | Number. Shown on the card and in the "In this room" total |
| `currency` | – | Overrides `currency` from the config for this row |
| `url` | – | Product page ("View product ↗") |
| `thumb` | – | Picture for the list. If empty, a thumbnail is rendered automatically |
| `tags` | – | Extra search words, separated by `;` |
| `sku` | – | Searchable, also works in `?add=` |

Excel files saved with `;` as the separator work too. In that case, separate tags with `|`.

**Performance with 200 items:**
- The catalogue file is small (one line per item) and loads once.
- Categories are collapsed. Cards and thumbnails are built only when a category is opened or a card scrolls into view.
- A `.glb` model downloads only when the item is placed in the room, or when its thumbnail is needed and no `thumb` picture is given. Give every model item a `thumb` image to avoid downloading models just for the list.
- Keep each model small: under ~2–3 MB, Draco compressed, textures ≤ 2048 px. Export from Onshape or other CAD as glTF/GLB, then compress with e.g. `gltf-transform optimize in.glb out.glb --compress draco`.

**"View in your room" button on a product page:** link to `index.html?add=oslo-sofa`. The planner opens with that product already placed. If the visitor has no room yet, it starts in a default 4 × 3.5 m room.

### Notes

- `catalogUrl` needs the page to be served over http(s). Browsers block `fetch` from `file://`.
- three.js 0.160.0 loads from `cdn.jsdelivr.net`, including the Draco decoder for compressed models. pdf.js 3.11.174 loads from `cdnjs.cloudflare.com`, and only when a PDF is uploaded. Both versions are pinned.
- Model files (`.glb`) must be served from the same site, or from a server that allows CORS.
- Wall auto-detection works best on clean architectural plans with filled or thick walls. If it misses walls or adds extra ones, change **Detect darkness** / **Min wall thickness**, delete the wrong pieces, or draw the walls by hand.
