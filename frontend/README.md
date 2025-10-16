# AI Lead Generation Platform - Frontend

A premium React/TypeScript frontend for the AI Lead Generation Platform, built with the Elvision Foundations design system.

## 🎨 Design System

- **Brand Colors**: Elvision teal (#139187) with sophisticated gradients
- **Typography**: Inter for UI, Poppins for headings, JetBrains Mono for code
- **Components**: shadcn/ui primitives with custom Elvision styling
- **Animations**: Framer Motion for smooth micro-interactions
- **Theme**: Light/dark mode support with seamless transitions

## 🚀 Features

### Core Components
- **AppShell**: Responsive sidebar navigation with theme toggle
- **Dashboard**: Metrics cards, charts, and activity feed
- **JobWizard**: 3-step job creation with targeting, quality, and prompt configuration
- **LeadsTable**: Advanced table with filtering, sorting, and batch actions
- **Design System**: Consistent components with glow effects and glass morphism

### Key Capabilities
- **Responsive Design**: Mobile-first with desktop optimization
- **Accessibility**: Full keyboard navigation and screen reader support
- **Performance**: Virtualized tables and optimized rendering
- **Real-time**: WebSocket integration ready for live updates
- **Export**: CSV, Google Sheets, and CRM integration support

## 🛠 Tech Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui** for component primitives
- **Framer Motion** for animations
- **Recharts** for data visualization
- **React Query** for data fetching
- **React Hook Form** with Zod validation
- **Radix UI** for accessible components

## 📦 Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🎯 Usage

### Development
```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`

### Production Build
```bash
npm run build
npm run preview
```

## 🎨 Design Tokens

The design system uses CSS custom properties for consistent theming:

```css
:root {
  --brand: 19,145,135;     /* #139187 */
  --bg: 250,250,250;       /* light background */
  --fg: 15,15,15;          /* foreground text */
  --muted: 108,115,120;    /* muted text */
  --card: 255,255,255;     /* card background */
  --glow: 19,145,135;      /* glow color */
  --radius: 14px;          /* border radius */
}
```

### Glow Effects
```css
.shadow-glow {
  box-shadow:
    0 0 0 1px rgba(var(--glow), .14),
    0 8px 30px rgba(var(--glow), .18);
}
```

## 🔧 Configuration

### Tailwind Config
The `tailwind.config.ts` includes:
- Custom brand color palette
- Glow shadow utilities
- Animation keyframes
- Font family configuration

### Component Structure
```
src/
├── components/
│   ├── ui/           # shadcn/ui components
│   ├── AppShell.tsx  # Main layout
│   ├── Dashboard.tsx # Dashboard page
│   ├── JobWizard.tsx # Job creation wizard
│   └── LeadsTable.tsx # Leads management
├── lib/
│   └── utils.ts      # Utility functions
└── main.tsx          # App entry point
```

## 🎯 Key Features

### Job Creation Wizard
- **Step 1**: Targeting (industry, location, company size, keywords)
- **Step 2**: Quality & Sources (threshold, data sources, verification)
- **Step 3**: Prompt & Output (AI prompt, target count, format)

### Leads Management
- **Advanced Filtering**: Status, source, date ranges
- **Batch Actions**: Export, verify, add to campaigns
- **Sorting**: All columns with visual indicators
- **Search**: Real-time search across all fields
- **Starring**: Favorite important leads

### Dashboard Analytics
- **Metrics Cards**: Key performance indicators
- **Charts**: Leads over time, source distribution
- **Activity Feed**: Real-time job and lead updates
- **Status Indicators**: System health and notifications

## 🚀 Deployment

The frontend is designed to work with the FastAPI backend:

1. **Development**: `npm run dev` (port 3000)
2. **Production**: `npm run build` → serve `dist/` folder
3. **Integration**: Configure API endpoints in environment variables

## 🎨 Customization

### Brand Colors
Update the color palette in `tailwind.config.ts`:

```typescript
colors: {
  brand: {
    DEFAULT: '#139187',
    50: '#e5f4f2',
    // ... full palette
  }
}
```

### Components
All components use the `cn()` utility for conditional styling:

```typescript
<Button className={cn("base-styles", condition && "conditional-styles")} />
```

## 📱 Responsive Design

- **Mobile**: Collapsible sidebar, touch-friendly interactions
- **Tablet**: Optimized layouts for medium screens
- **Desktop**: Full feature set with advanced interactions

## ♿ Accessibility

- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: ARIA labels and semantic HTML
- **Color Contrast**: WCAG AA compliant
- **Focus Management**: Visible focus indicators

## 🔄 State Management

- **Local State**: React hooks for component state
- **Global State**: React Query for server state
- **Form State**: React Hook Form with Zod validation
- **URL State**: React Router for navigation

## 🎯 Performance

- **Code Splitting**: Route-based lazy loading
- **Virtual Scrolling**: For large datasets
- **Memoization**: React.memo and useMemo
- **Bundle Optimization**: Tree shaking and minification

---

**Built with ❤️ for Elvision Foundations**
