# Real-Time Notifications Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SWAPSHIFT APPLICATION                    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            NotificationProvider (Context)             │  │
│  │  ├─ swapRequests: []                                 │  │
│  │  ├─ unreadCount: 0                                   │  │
│  │  └─ updateSwapRequests(): void                       │  │
│  └──────────────────────────────────────────────────────┘  │
│           ▲                                                  │
│           │ Wraps all routes                                │
│           │                                                  │
│  ┌────────┴─────────────────────────────────────────────┐  │
│  │           EmployeeDashboard Component                │  │
│  │                                                      │  │
│  │  useNotifications(enabled, pollInterval)            │  │
│  │        ↓                                             │  │
│  │   Every 2 seconds:                                  │  │
│  │   1. GET /api/v1/swap/inbox                         │  │
│  │   2. Compare with previous count                    │  │
│  │   3. If new requests → trigger alerts               │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                       ▲                                      │
│                       │                                      │
│        ┌──────────────┼──────────────┐                      │
│        ▼              ▼              ▼                      │
│   ┌────────┐   ┌────────┐   ┌──────────────┐              │
│   │ Beep   │   │ Toast  │   │   Desktop    │              │
│   │ Sound  │   │Message │   │Notification │              │
│   │ 800Hz  │   │3s fade │   │  Requires    │              │
│   │500ms   │   │out     │   │Permission   │              │
│   └────────┘   └────────┘   └──────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Person B sends swap request
        ↓
Backend: POST /api/v1/swap/request
  ├─ Saves request to database
  └─ (Notification sent via WhatsApp/email separately)
        ↓
Frontend: Every 2 seconds
  ├─ GET /api/v1/swap/inbox [Person A]
  └─ Response: [{ request_id: 1, ... }, { request_id: 2, ... }]
        ↓
useNotifications Hook
  ├─ Compare count: 2 > 0? YES!
  ├─ Call updateSwapRequests([...])
  ├─ Play sound: playNotificationSound()
  ├─ Show toast: showToast("You have 2 new swap requests!")
  └─ Show notification: new Notification("🔔 SwapShift Alert")
        ↓
Person A SEES:
  ├─ 🔔 Beep (audio)
  ├─ 📬 Toast message (UI)
  └─ 🔔 Browser notification (system)
        ↓
✓ All without refresh or re-login!
```

## Component Structure

```
App.jsx
 ├─ Router
 │   ├─ AuthProvider
 │   │   ├─ ToastProvider
 │   │   │   └─ NotificationProvider ← Wraps everything
 │   │   │       ├─ AuthPage
 │   │   │       ├─ PendingApproval
 │   │   │       ├─ EmployeeDashboard
 │   │   │       │   └─ useNotifications() ← Polling starts here
 │   │   │       └─ AdminDashboard
 │   │   │
 │   │   └─ Toast Container
 │   │       └─ Toast Components
```

## State Management

```
NotificationContext
├─ swapRequests: Array
│   Example: [
│     { request_id: 1, from_employee: "E001", to_shift: "Morning" },
│     { request_id: 2, from_employee: "E002", to_shift: "Evening" }
│   ]
│
├─ unreadCount: Number
│   Example: 2
│
├─ lastNotification: Object
│   Example: { timestamp: 1234567890, count: 2 }
│
└─ Methods:
    ├─ updateSwapRequests(requests)
    ├─ markAsRead()
    └─ recordNotification(notification)
```

## API Integration

```
Frontend                    Backend
   │                           │
   ├─ GET /api/v1/swap/inbox ──┤
   │                           │
   │  Response: {              │
   │    "data": [              │
   │      {                     │
   │        "request_id": 1,    │
   │        "from_id": "E001",  │
   │        "to_date": "2024...",
   │        "shift": "Morning"  │
   │      },                    │
   │      ...                   │
   │    ]                       │
   │  }                         │
   │<──────────────────────────┤
   │                           │
   │ (Repeat every 2 seconds)  │
```

## Notification Priority & Behavior

```
┌─────────────────────────────────────────┐
│  3 LAYERS OF NOTIFICATIONS               │
├─────────────────────────────────────────┤
│                                         │
│  LAYER 1: Audio Beep 🔔                │
│  ├─ Always plays (if browser volume on)│
│  ├─ Frequency: 800Hz (configurable)   │
│  ├─ Duration: 500ms                   │
│  ├─ Purpose: Immediate attention      │
│  └─ Fallback: Works if UI has issues  │
│                                         │
│  LAYER 2: Toast Message 📬             │
│  ├─ Always shows                       │
│  ├─ Position: Bottom-right             │
│  ├─ Auto-dismiss: 3 seconds           │
│  ├─ Content: "You have X new requests"│
│  └─ Click: Navigates to inbox         │
│                                         │
│  LAYER 3: Desktop Notification 🔔     │
│  ├─ Requires permission                │
│  ├─ Shows in taskbar/system tray      │
│  ├─ Requires interaction (click)       │
│  ├─ Shows even if browser minimized   │
│  └─ Tag: 'swap-request-notification'  │
│                                         │
└─────────────────────────────────────────┘
```

## Timeline Example

```
TIME    PERSON A                  PERSON B           BACKEND
────────────────────────────────────────────────────────────
10:00   Login, Dashboard loads    
        useNotifications starts
        
10:02                             Clicks "Request Swap"
                                  Selects Person A
                                                    POST /swap/request
                                                    ✓ Saved to DB
                                  ✓ Confirmation

10:02   (No notification yet)
+1s     (Still browsing)

10:02   GET /swap/inbox
+2s     Count: 1 (new!)
        ╔════════════════════════╗
        ║ 🔔 BEEP (800Hz, 500ms) ║
        ╠════════════════════════╣
        ║ 📬 Toast: "1 new       ║
        ║    request!"           ║
        ║ 🔔 Desktop             ║
        ║    notification        ║
        ╚════════════════════════╝

10:02   ✓ Sees notification
+2.5s   (Without refresh!)

10:03   Inbox shows new request
        Person A can accept/reject
```

## Performance Impact

```
Resource Usage Per Poll:
┌─────────────────────────────┐
│ Network: ~5KB per request   │
│ Processing: <10ms          │
│ Audio: <1KB (generated)    │
│ Total Overhead: Minimal    │
└─────────────────────────────┘

Polling Schedule:
┌─────────────────────────────┐
│ Frequency: Every 2 seconds │
│ Duration: User session     │
│ Stops on: Page unload      │
│ Pauses on: Tab inactive*   │
└─────────────────────────────┘
*Can be optimized with Page Visibility API
```

## Security & Privacy

```
✓ SECURE FEATURES:
├─ Token included in every request
├─ 401 errors handled (re-login)
├─ No sensitive data in notifications
├─ Read-only operations (no POST/PUT)
├─ User-initiated permission (notifications)
├─ CORS protected (same-origin only)
└─ Rate limited by polling interval

✓ USER PRIVACY:
├─ Polling data cached locally
├─ No external services (except backend)
├─ Browser notifications optional
├─ Sound can be disabled
├─ Toast can be dismissed
└─ Notification history not stored
```

## Browser Compatibility

```
FEATURE SUPPORT:
┌──────────────┬──────┬─────────┬────────┬──────┐
│ Feature      │Chrome│ Firefox │ Safari │ Edge │
├──────────────┼──────┼─────────┼────────┼──────┤
│ Audio API    │  ✅  │   ✅    │   ✅   │  ✅  │
│ Fetch API    │  ✅  │   ✅    │   ✅   │  ✅  │
│ Notification │  ✅  │   ✅    │   ✅   │  ✅  │
│ localStorage │  ✅  │   ✅    │   ✅   │  ✅  │
│ Promises     │  ✅  │   ✅    │   ✅   │  ✅  │
└──────────────┴──────┴─────────┴────────┴──────┘

GRADE: ✅ Fully Supported
```

## Alternative Approaches (Considered)

```
1. WebSocket (Real-time, 0ms latency)
   ✓ Pros: Instant updates
   ✗ Cons: Complex setup, server load
   
2. Polling (Current, 2s latency)
   ✓ Pros: Simple, works everywhere
   ✓ Cons: Slight delay, uses more requests
   ✓ CHOSEN FOR: Simplicity + effectiveness

3. Server-Sent Events (SSE)
   ✓ Pros: Real-time, simpler than WebSocket
   ✗ Cons: Limited browser support, firewall issues
   
4. Native Notifications (Optional future)
   ✓ Pros: Phone/desktop app integration
   ✗ Cons: Requires native app, complex
```

## Future Enhancements

```
PHASE 1 (Current):
├─ Polling-based notifications ✓
├─ Audio + Toast + Desktop alerts ✓
└─ Works without refresh ✓

PHASE 2 (Optional):
├─ Notification preferences
├─ Sound selection
├─ Do Not Disturb mode
└─ Notification history

PHASE 3 (Advanced):
├─ WebSocket for real-time
├─ Service Worker for offline
├─ Mobile push notifications
├─ Analytics tracking
└─ Notification encryption
```

## Monitoring & Debugging

```
To check if notifications are working:

1. Browser DevTools (F12):
   Console → Look for:
   - "Notification permission granted"
   - Network → GET /api/v1/swap/inbox (every 2s)
   - No red errors

2. Network Tab:
   - Should see requests every 2 seconds
   - Response status: 200 OK
   - Response body: JSON array

3. Application Tab:
   - localStorage: token, role, user
   - sessionStorage: (as needed)

4. Check logs:
   - No 401 errors (auth failure)
   - No CORS errors
   - No Uncaught exceptions
```

---

This architecture ensures **reliable, real-time notifications** without requiring:
- Page refresh
- Re-login
- Manual intervention
- Complex setup
