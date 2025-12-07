# RoboBrain 2.0 - Testing Checklist

## Pre-Testing Setup
- [ ] Backend running on port 5001
- [ ] Frontend dev server running
- [ ] Groq API key configured
- [ ] CUDA available and working

## Chat History Testing

### Session Creation & Restoration
- [ ] Start fresh (clear localStorage)
- [ ] Send a message
- [ ] Verify auto-save in localStorage (check DevTools → Application → Local Storage)
- [ ] Refresh page
- [ ] Verify session and messages restored
- [ ] Check console logs for "Restored session: ..." message

### New Chat Button
- [ ] Start a conversation with 3-4 messages
- [ ] Click "New Chat" button
- [ ] Verify old session is saved
- [ ] Verify new empty session created
- [ ] Verify currentImage and currentTask reset

### History Viewer
- [ ] Create 2-3 different conversations
- [ ] Click History button (clock icon) in header
- [ ] Verify modal shows all sessions
- [ ] Check timestamps display correctly
- [ ] Verify preview text shows last user message
- [ ] Check task badges display correctly
- [ ] Verify image icon shows when session has images

### Load Previous Session
- [ ] Open History modal
- [ ] Click on a previous session
- [ ] Verify session loads correctly
- [ ] Verify all messages display
- [ ] Verify images display if present
- [ ] Verify modal closes after loading

### Delete Session
- [ ] Open History modal
- [ ] Click delete button on a session
- [ ] Verify confirmation dialog appears
- [ ] Confirm deletion
- [ ] Verify session removed from list
- [ ] Verify localStorage updated

## Auto Mode Testing

### Task Detection
- [ ] Select "Auto Mode" task
- [ ] Upload robot image
- [ ] Ask "what objects are in this image?" → Should detect as grounding
- [ ] Ask "how can I grasp this?" → Should detect as affordance
- [ ] Ask "plan a path to pick this up" → Should detect as trajectory
- [ ] Ask "where should I touch this?" → Should detect as pointing
- [ ] Ask "describe what you see" → Should detect as general

### UI Feedback
- [ ] Verify sparkle icon ✨ shows on auto-detected messages
- [ ] Verify task badge displays detected task
- [ ] Check console for "Auto-detected task: X" logs

## Image Processing

### Upload & Resize
- [ ] Upload small image (<2000px) → No resize needed
- [ ] Upload large image (>2000px) → Should auto-resize
- [ ] Verify resized image displays in sidebar
- [ ] Check console for resize logs

### Annotation Display
- [ ] Test grounding task → Should show bounding boxes
- [ ] Test trajectory task → Should show path lines
- [ ] Test pointing task → Should show points
- [ ] Test affordance task → Should show highlighted areas
- [ ] Verify annotations visible on output images

### Backend vs Frontend Annotation
- [ ] Send grounding request with valid coordinates
- [ ] Verify backend annotates correctly
- [ ] Manually test with invalid coordinate format
- [ ] Verify frontend fallback annotation works

## Memory Management

### GPU Memory
- [ ] Send multiple requests in sequence
- [ ] Monitor GPU memory usage (nvidia-smi)
- [ ] Verify memory doesn't exceed 4.8GB
- [ ] Check cleanup happens after each request

### Large Image Handling
- [ ] Upload 4K image → Should resize to 2000px
- [ ] Upload 8K image → Should resize to 2000px
- [ ] Verify no OOM errors occur
- [ ] Check inference completes successfully

## Dark Mode

### Theme Switching
- [ ] Click dark mode toggle
- [ ] Verify entire UI switches to dark theme
- [ ] Verify localStorage persists preference
- [ ] Refresh page → Theme should persist
- [ ] Toggle back to light mode
- [ ] Verify smooth transition

## Error Handling

### Backend Offline
- [ ] Stop backend server
- [ ] Verify "Offline" status in header
- [ ] Try sending message
- [ ] Verify error handling gracefully

### Invalid Image
- [ ] Upload non-image file → Should reject
- [ ] Upload corrupted image → Should handle error
- [ ] Verify error messages display

### Empty Messages
- [ ] Try sending empty message → Should be disabled/blocked
- [ ] Try sending message without image when needed

## Performance

### Response Time
- [ ] Measure time for general chat (~5-10s expected)
- [ ] Measure time for grounding task (~10-15s expected)
- [ ] Measure time for trajectory task (~10-15s expected)
- [ ] Verify "Thinking..." indicator shows

### UI Responsiveness
- [ ] Scroll through long conversations
- [ ] Switch tasks multiple times
- [ ] Upload/remove images repeatedly
- [ ] Verify no UI lag or freezing

## Cross-Browser Testing
- [ ] Test on Chrome
- [ ] Test on Firefox
- [ ] Test on Edge
- [ ] Verify localStorage works on all browsers

## Known Issues to Verify

### Fixed Issues (Should NOT occur)
- [ ] Images not loading → Fixed with VITE_API_URL prepend
- [ ] CUDA OOM errors → Fixed with 8-bit quantization
- [ ] Coordinates not parsing → Fixed with improved regex
- [ ] Large images crashing → Fixed with auto-resize

### Expected Behaviors
- [ ] First inference takes longer (model loading)
- [ ] Concurrent requests queued (thread locks)
- [ ] History stored locally only (no server backup)

## Cleanup Testing
- [ ] Clear all localStorage data
- [ ] Verify fresh session created
- [ ] Verify no errors on empty history
- [ ] Verify New Chat works without prior sessions

## Documentation Verification
- [ ] README.md is up-to-date
- [ ] SYSTEM_OVERVIEW.md covers all features
- [ ] API endpoints documented
- [ ] Environment setup instructions clear

## Final Checks
- [ ] All git changes committed
- [ ] No console errors in browser
- [ ] No Python errors in backend
- [ ] All features working as expected
- [ ] Code formatted and clean
- [ ] Comments added where needed

## Test Results Template

```
Date: ___________
Tester: _________
Environment: _____

✅ Passed Tests: ____ / ____
❌ Failed Tests: ____ / ____

Issues Found:
1. ___________________
2. ___________________
3. ___________________

Notes:
_____________________
_____________________
_____________________
```

## Automated Testing (Future)
- [ ] Add Jest tests for frontend utilities
- [ ] Add pytest tests for backend endpoints
- [ ] Add E2E tests with Playwright
- [ ] Add CI/CD pipeline
