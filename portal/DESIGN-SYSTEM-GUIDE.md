# EnMS Design System - Quick Reference Guide

**Version:** 1.0  
**Created:** October 16, 2025  
**File:** `/portal/public/css/enms-design-system.css`

---

## 📦 How to Use

Add to your HTML `<head>`:

```html
<link rel="stylesheet" href="/css/enms-design-system.css">
```

---

## 🎨 Color Palette

### Primary Colors
- `--color-primary`: #667eea (Main brand purple)
- `--color-secondary`: #764ba2 (Secondary purple)

### Status Colors
- `--color-success`: #10b981 (Green)
- `--color-warning`: #f59e0b (Orange)
- `--color-error`: #ef4444 (Red)
- `--color-info`: #3b82f6 (Blue)

### Usage in CSS
```css
.my-element {
    color: var(--color-primary);
    background: var(--gradient-primary);
}
```

---

## 📏 Layout Components

### Container
```html
<div class="enms-container">
    <!-- Max-width 1200px, centered -->
</div>
```

### Grid System
```html
<div class="enms-grid enms-grid-4">
    <!-- 4 equal columns, responsive -->
</div>
```

### Flex Utilities
```html
<div class="enms-flex-between">
    <span>Left</span>
    <span>Right</span>
</div>
```

---

## 🧭 Navigation Bar

```html
<nav class="enms-nav">
    <div class="enms-nav-container">
        <a href="/" class="enms-nav-brand">
            ⚡ EnMS
        </a>
        <ul class="enms-nav-menu">
            <li class="enms-nav-item">
                <a href="/" class="enms-nav-link active">Dashboard</a>
            </li>
            <li class="enms-nav-item">
                <a href="/analytics" class="enms-nav-link">Analytics</a>
            </li>
            <li class="enms-nav-item">
                <a href="/grafana/" class="enms-nav-link">Grafana</a>
            </li>
        </ul>
    </div>
</nav>
```

---

## 🎴 Card Components

### Basic Card
```html
<div class="enms-card">
    <div class="enms-card-header">
        <h3 class="enms-card-title">Card Title</h3>
        <p class="enms-card-subtitle">Subtitle text</p>
    </div>
    <div class="enms-card-body">
        Card content goes here
    </div>
    <div class="enms-card-footer">
        <button class="enms-btn enms-btn-primary">Action</button>
    </div>
</div>
```

### Stat Card (for Dashboard)
```html
<div class="enms-stat-card">
    <div class="enms-stat-icon">⚙️</div>
    <span class="enms-stat-value" id="machine-count">7</span>
    <div class="enms-stat-label">Active Machines</div>
    <div class="enms-stat-change positive">↑ 2 from yesterday</div>
</div>
```

### Status Card with Color
```html
<div class="enms-card enms-card-success">
    <!-- Green border on left -->
</div>
```

---

## 🔘 Buttons

```html
<!-- Primary Button -->
<button class="enms-btn enms-btn-primary">Primary</button>

<!-- Success Button -->
<button class="enms-btn enms-btn-success">Success</button>

<!-- Outline Button -->
<button class="enms-btn enms-btn-outline">Outline</button>

<!-- Ghost Button -->
<button class="enms-btn enms-btn-ghost">Ghost</button>

<!-- Sizes -->
<button class="enms-btn enms-btn-primary enms-btn-sm">Small</button>
<button class="enms-btn enms-btn-primary enms-btn-lg">Large</button>

<!-- With Icon -->
<button class="enms-btn enms-btn-primary">
    🚀 Launch
</button>
```

---

## 🏷️ Badges & Status

### Badge
```html
<span class="enms-badge enms-badge-success">Active</span>
<span class="enms-badge enms-badge-warning">Warning</span>
<span class="enms-badge enms-badge-error">Error</span>
```

### Status Dot (Real-Time Indicators)
```html
<span class="enms-status-dot online"></span> System Online
<span class="enms-status-dot offline"></span> System Offline
<span class="enms-status-dot warning"></span> Warning
```

---

## 📊 Header & Hero

```html
<header class="enms-header">
    <h1>EnMS Portal</h1>
    <p>Energy Management System Dashboard</p>
</header>
```

---

## 📢 Alerts

```html
<div class="enms-alert enms-alert-success">
    ✓ Operation completed successfully
</div>

<div class="enms-alert enms-alert-warning">
    ⚠ Warning message here
</div>

<div class="enms-alert enms-alert-error">
    ✗ Error message here
</div>
```

---

## ⚙️ Loading States

### Spinner
```html
<div class="enms-loading"></div>
```

### Skeleton (for loading cards)
```html
<div class="enms-skeleton" style="height: 200px;"></div>
```

### Pulse Animation (real-time data)
```html
<span class="enms-pulse">Live Data</span>
```

---

## 🛠️ Utility Classes

### Text
```html
<p class="text-center">Centered text</p>
<p class="text-primary">Primary color text</p>
<p class="font-bold">Bold text</p>
```

### Spacing
```html
<div class="mt-4">Margin top</div>
<div class="mb-6">Margin bottom</div>
<div class="p-4">Padding all sides</div>
```

### Display
```html
<div class="hidden">Hidden</div>
<div class="hidden-mobile">Hidden on mobile</div>
<div class="hidden-desktop">Hidden on desktop</div>
```

---

## 🎬 Animations

```html
<div class="enms-fade-in">Fades in</div>
<div class="enms-slide-up">Slides up</div>
<div class="enms-pulse">Pulses (real-time indicator)</div>
```

---

## 📱 Responsive Breakpoints

- **Mobile**: < 768px
- **Desktop**: ≥ 769px

Grids automatically collapse to single column on mobile.

---

## 🎯 Common Patterns

### Dashboard Stats Row
```html
<div class="enms-grid enms-grid-4">
    <div class="enms-stat-card">
        <div class="enms-stat-icon">⚙️</div>
        <span class="enms-stat-value">7</span>
        <div class="enms-stat-label">Active Machines</div>
    </div>
    <!-- Repeat for other stats -->
</div>
```

### Page Layout with Navigation
```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/css/enms-design-system.css">
</head>
<body>
    <nav class="enms-nav">...</nav>
    
    <header class="enms-header">
        <h1>Page Title</h1>
    </header>
    
    <div class="enms-container">
        <div class="enms-grid enms-grid-2">
            <div class="enms-card">...</div>
            <div class="enms-card">...</div>
        </div>
    </div>
    
    <footer class="enms-footer">
        <p>&copy; 2025 EnMS</p>
    </footer>
</body>
</html>
```

---

## 💡 Tips

1. **Consistency**: Use design system classes instead of custom CSS
2. **Real-Time**: Add `enms-pulse` class to live data indicators
3. **Status**: Use `enms-status-dot` for connection status
4. **Cards**: Always hover-transform creates nice UX
5. **Mobile**: Test on mobile - grids auto-collapse

---

## 🔗 Next Steps

1. **Apply to landing page** - Replace inline styles
2. **Add navigation bar** - Use `enms-nav` component
3. **Add WebSocket indicators** - Use `enms-pulse` and `enms-status-dot`

---

**Questions?** Check the CSS file comments for detailed documentation!
