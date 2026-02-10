# 🎨 Theme Comparison Guide

## Two New Themes to Test Group Heading Colors

I've created two experimental themes to solve the "group heading visibility" problem:

---

## 🔥 **Burnt Orange Pro V2** - Two-Tone Orange System

### Color Strategy:
- **Group headings** (Client/Project/Task rows) = **Light Peach/Salmon** `#f4a460`
- **Selected entries** = **Full Burnt Orange** `#ce6427`
- **Column headers** = **Full Burnt Orange** `#ce6427`

### Visual Hierarchy:
```
🔶 BURNT ORANGE Headers (Hierarchy | Type | Details | etc.)
├─ 🍑 LIGHT PEACH   Client: Novel Crafting
│  ├─ 🍑 LIGHT PEACH   Project: The Ink and Incense
│  │  ├─ 🍑 LIGHT PEACH   Task: Writing
│  │  │  ├─ ⬜ WHITE Entry (clickable)
│  │  │  └─ 🔶 ORANGE Entry (when SELECTED)
```

### Pros:
- ✅ Stays 100% brand consistent (all orange family)
- ✅ Clear hierarchy (light vs bright orange)
- ✅ Soft on eyes (peachy groups aren't harsh)
- ✅ Works with website color scheme

### Cons:
- ⚠️ Might still feel "too orange" when many items selected
- ⚠️ Light peach might blend with taupe background slightly

---

## 🌊 **Burnt Orange Pro V3** - Orange + Teal Contrast

### Color Strategy:
- **Group headings** (Client/Project/Task rows) = **Muted Teal** `#5a8f8f`
- **Selected entries** = **Full Burnt Orange** `#ce6427`
- **Column headers** = **Full Burnt Orange** `#ce6427`

### Visual Hierarchy:
```
🔶 BURNT ORANGE Headers (Hierarchy | Type | Details | etc.)
├─ 🌊 MUTED TEAL   Client: Novel Crafting
│  ├─ 🌊 MUTED TEAL   Project: The Ink and Incense
│  │  ├─ 🌊 MUTED TEAL   Task: Writing
│  │  │  ├─ ⬜ WHITE Entry (clickable)
│  │  │  └─ 🔶 ORANGE Entry (when SELECTED)
```

### Pros:
- ✅ **STRONG** visual contrast (teal ≠ orange)
- ✅ Complementary colors (color theory approved!)
- ✅ Teal feels professional/modern
- ✅ Orange selections really POP against teal groups
- ✅ No confusion between groups and selected items

### Cons:
- ⚠️ Introduces new color (not pure orange branding)
- ⚠️ Teal might clash with your website (which is all orange/taupe)
- ⚠️ More complex color palette

---

## 🎯 My Recommendation

**Try V3 (Orange + Teal) first** because:

1. **Solves the problem better** - Much clearer distinction
2. **Your screenshots** show the confusion is real - need strong contrast
3. **Teal is subtle** - It's muted, not bright/loud
4. **You can always fall back** to V2 if you hate the teal

---

## ⚠️ IMPORTANT NOTE

**These themes are created BUT won't work yet** because the GUI code needs to be updated to actually apply the `group_heading` color to those rows.

**Next step:** I need to find where in `gui.py` the group rows are inserted and add tag configuration to color them.

---

## 🧪 Once Fixed, Test Like This:

1. **Restart app**
2. **Company Info > Appearance**
3. Try **"Burnt Orange Pro V3"** (teal groups)
4. Go to **Time Entries tab** and **Invoices tab**
5. Look at the group rows (Client/Project/Task)
6. Select some entries
7. **Does it feel clear?**
8. Switch to **"Burnt Orange Pro V2"** (light peach groups)
9. Compare side-by-side
10. Pick your favorite!

---

## 🔧 What I Need to Do Next

1. Find where `gui.py` inserts Client/Project/Task rows into treeviews
2. Add tag configuration: `tree.tag_configure('group', background=self.colors['group_heading'])`
3. Apply the tag when inserting group rows
4. Test both themes

**Want me to do that now?** Or do you need a break? 😊
