# ExpandableBlock Component - P2 Completion

**Date:** 2026-01-05
**Status:** Completed
**Priority:** P2

## Summary

Created a generic, reusable `ExpandableBlock` component that implements the expand/collapse card pattern used across the library feature. This component provides a consistent API for building expandable card UIs.

## Analysis

After reviewing the existing block components:

| Component | Lines | Pattern | Consolidatable? |
|-----------|-------|---------|-----------------|
| `collapsible-block.tsx` | 149 | Expand/collapse with list | Yes |
| `highlights-block.tsx` | 150 | Auto-carousel/slideshow | No (different pattern) |
| `librarian-block.tsx` | 268 | Two-panel navigation | No (different pattern) |

The `HighlightsBlock` is a carousel component and `LibrarianBlock` uses a two-panel navigation pattern. These are fundamentally different from the expand/collapse pattern, so they were not consolidated.

The new `ExpandableBlock` component captures the expand/collapse pattern that can be reused for similar UIs.

## Created Component

**`src/components/ui/expandable-block.tsx`** (205 lines)

### Features

- **Expand/collapse animation** with Framer Motion
- **Configurable header** with icon, title, subtitle, badge
- **Preview content** shown when collapsed
- **Expanded content** shown when expanded
- **"View All" link** with customizable text
- **Variants**: `default`, `compact`, `featured`
- **Width control** for fixed-width layouts
- **Event callback** for expand state changes

### Sub-components

- `ExpandableBlockItem` - Animated list item with icon and text
- `ExpandableBlockList` - Container for list items with proper spacing

## Usage

```tsx
import {
  ExpandableBlock,
  ExpandableBlockList,
  ExpandableBlockItem
} from "@/components/ui/expandable-block"
import { Folder, File } from "lucide-react"

// Basic usage
<ExpandableBlock
  title="Recent Files"
  subtitle="5 items"
  icon={<Folder className="h-5 w-5" />}
  badge={5}
  viewAllLink="/library/files"
  expandedContent={
    <ExpandableBlockList>
      <ExpandableBlockItem
        icon={<File className="h-5 w-5" />}
        primary="Document.pdf"
        secondary="2 hours ago"
        index={0}
      />
      <ExpandableBlockItem
        icon={<File className="h-5 w-5" />}
        primary="Report.docx"
        secondary="Yesterday"
        index={1}
      />
    </ExpandableBlockList>
  }
/>

// With variants
<ExpandableBlock
  title="Featured"
  variant="featured"  // Adds primary border color
  width={380}        // Fixed width
  defaultExpanded    // Start expanded
  onExpandChange={(expanded) => console.log('Expanded:', expanded)}
  expandedContent={...}
/>

// Compact variant
<ExpandableBlock
  title="Quick Actions"
  variant="compact"
  expandedContent={...}
/>
```

## Props Reference

### ExpandableBlock

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | required | Block title |
| `subtitle` | `string` | - | Optional subtitle |
| `icon` | `ReactNode` | - | Header icon |
| `badge` | `string \| number` | - | Badge content |
| `children` | `ReactNode` | - | Preview content (shown when collapsed) |
| `expandedContent` | `ReactNode` | - | Content shown when expanded |
| `defaultExpanded` | `boolean` | `false` | Start expanded |
| `viewAllLink` | `string` | - | Link for View All button |
| `viewAllText` | `string` | `"View All"` | View All button text |
| `variant` | `"default" \| "compact" \| "featured"` | `"default"` | Visual variant |
| `width` | `string \| number` | - | Fixed width |
| `className` | `string` | - | Additional classes |
| `onExpandChange` | `(expanded: boolean) => void` | - | Expand state callback |

### ExpandableBlockItem

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `icon` | `ReactNode` | - | Item icon |
| `primary` | `string` | required | Primary text |
| `secondary` | `string` | - | Secondary text |
| `onClick` | `() => void` | - | Click handler |
| `index` | `number` | `0` | Animation delay index |

## Migration Example

```tsx
// Before: Using CollapsibleBlock directly
<CollapsibleBlock
  title="Collections"
  items={items}
  iconUrls={iconUrls}
  viewAllLink="/collections"
/>

// After: Using ExpandableBlock
<ExpandableBlock
  title="Collections"
  subtitle={`${items.length} items`}
  viewAllLink="/collections"
  viewAllText="View Collections"
  width={380}
  expandedContent={
    <ExpandableBlockList>
      {items.map((item, index) => (
        <ExpandableBlockItem
          key={item.id}
          icon={<Image src={item.icon} alt="" className="h-5 w-5" />}
          primary={item.name}
          secondary={item.secondaryText}
          index={index}
        />
      ))}
    </ExpandableBlockList>
  }
/>
```

## Verification

```bash
npx tsc --noEmit  # TypeScript compilation passes
```

## Impact

| Metric | Value |
|--------|-------|
| New component | 205 lines |
| Reusable pattern | Expand/collapse card |
| Potential adoption | ~5-10 similar UIs |

## Next Steps

1. **Migrate CollapsibleBlock** to use ExpandableBlock internally
2. **Document in Storybook** (if available) for design system
3. **Consider accessibility** (keyboard navigation, ARIA attributes)

## Notes

The original refactoring proposal suggested consolidating all three block components (collapsible, highlights, librarian) into one. However, after analysis:

- `HighlightsBlock` is a carousel (fundamentally different pattern)
- `LibrarianBlock` has two-panel navigation (fundamentally different pattern)

These components solve different UI problems and should remain separate. The new `ExpandableBlock` captures the common expand/collapse pattern that can be reused elsewhere.
