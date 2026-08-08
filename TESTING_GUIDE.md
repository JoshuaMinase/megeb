# Testing Guide - Food Images & YouTube Links

## Local Testing Steps

### 1. Reseed the Database

```bash
# Navigate to backend directory
cd backend

# Run the seed script to populate MongoDB with updated recipes
python seed_data.py

# Expected output:
# Seeded 35 recipes.
```

### 2. Start the Backend Server

```bash
# In backend directory, start the FastAPI server
python main.py

# Server will run at http://localhost:8000
# API documentation available at http://localhost:8000/docs
```

### 3. View in Browser

1. Open `http://localhost:3000` (or wherever frontend is running)
2. Navigate to **"Foods"** page
3. Select any food dish (e.g., "Doro Wat")
4. Scroll down to see:
   - **Recipe ingredients** with your food image
   - **📺 Video Tutorial** section with embedded YouTube player
   - **Preparation Method** steps

### 4. Test Features

#### Image Display
- [ ] Recipe image loads without errors
- [ ] Image is high-quality and shows actual food
- [ ] Image is different for each recipe (not duplicated)
- [ ] Image works on mobile (responsive)

#### YouTube Video
- [ ] Video tutorial section appears below ingredients
- [ ] Section header shows "📺 Video Tutorial"
- [ ] Embedded video player displays correctly
- [ ] Video player is responsive and maintains 16:9 aspect ratio
- [ ] Video controls work (play, pause, fullscreen)
- [ ] Video doesn't autoplay

#### Responsive Design
- [ ] Test on mobile phone (375px width)
- [ ] Test on tablet (768px width)
- [ ] Test on desktop (1920px width)
- [ ] Video maintains correct aspect ratio on all sizes

---

## API Testing

### Using curl to test API

#### Get a Recipe
```bash
# Get first recipe from API
curl http://localhost:8000/recipes/trending?limit=1

# Response should include:
# - image: "https://images.unsplash.com/..."
# - youtube_url: "https://www.youtube.com/watch?v=..."
```

#### Search Recipes
```bash
# Search for recipes
curl "http://localhost:8000/recipes/search/q?q=doro"

# All results should have:
# - image field with real URLs
# - youtube_url field with YouTube links
```

### Using API Documentation

1. Visit http://localhost:8000/docs
2. Expand "recipes" endpoints
3. Click "Try it out" on any endpoint
4. Execute and verify:
   - All recipes include `image` URLs (no "images/" paths)
   - All recipes include `youtube_url` links
   - No errors in response

---

## Database Verification

### MongoDB Shell Commands

```javascript
// Connect to MongoDB
mongosh mongodb://localhost:27017/megeb

// Verify recipes are seeded
db.recipes.countDocuments()
// Should return: 35

// Check first recipe has required fields
db.recipes.findOne({name: "Doro Wat"})
// Should show:
// - image: "https://images.unsplash.com/..."
// - youtube_url: "https://www.youtube.com/watch?v=..."

// Verify no local paths remain
db.recipes.countDocuments({image: /^images\//})
// Should return: 0

// Verify all recipes have youtube_url
db.recipes.countDocuments({youtube_url: {$exists: true, $ne: ""}})
// Should return: 35 (or close to it, some might be empty string)
```

---

## Visual Testing Checklist

### Desktop Browser (Chrome, Firefox, Safari)
- [ ] Recipe page loads correctly
- [ ] Image displays above ingredients section
- [ ] Video section appears with "📺 Video Tutorial" header
- [ ] Embedded iframe loads (no broken video)
- [ ] Page layout is clean and organized
- [ ] All text is readable
- [ ] Colors match site design

### Mobile Browser (iOS Safari, Chrome Mobile)
- [ ] Page loads quickly
- [ ] Images scale properly
- [ ] Video player is responsive
- [ ] Video maintains 16:9 ratio
- [ ] Touch controls work (play, pause)
- [ ] Video can go fullscreen
- [ ] No layout breakage

### Tablets (iPad, Android tablet)
- [ ] Content displays well
- [ ] Not too compressed or stretched
- [ ] Video is viewable without scrolling too much
- [ ] Text is readable

---

## Edge Case Testing

### Videos Not Available
1. Edit `seed_data.py` and comment out a youtube_url
2. Reseed database
3. Visit recipe - should NOT show video section
4. Verify page still loads correctly

### Missing Images
1. Edit `seed_data.py` and set an image URL to empty string
2. Reseed database
3. Visit recipe - should show fallback image or no image
4. Verify page doesn't break

### YouTube URL Variations
Test that `extractYouTubeId()` handles these formats:
- `https://www.youtube.com/watch?v=wO_-xP2k9yE` ✓
- `https://youtu.be/wO_-xP2k9yE` ✓
- `https://www.youtube.com/embed/wO_-xP2k9yE` ✓
- `https://www.youtube.com/watch?v=wO_-xP2k9yE&t=10s` ✓

---

## Performance Testing

### Image Loading
- [ ] Images load within 2 seconds
- [ ] No layout shift when images load
- [ ] Proper use of CDN (Unsplash)

### Video Loading
- [ ] iframe loads within 2 seconds
- [ ] No autoplay delays
- [ ] Video metadata loads correctly

### Page Load Time
- [ ] Recipe page loads in under 3 seconds
- [ ] No blocking resources
- [ ] Responsive images

---

## Accessibility Testing

### Keyboard Navigation
- [ ] Can tab through video player controls
- [ ] Play/pause work with keyboard
- [ ] Fullscreen works with keyboard

### Screen Reader (NVDA, JAWS, VoiceOver)
- [ ] Image alt text is present
- [ ] Video iframe has proper ARIA labels
- [ ] Video description is accessible

### Color Contrast
- [ ] Video section text is readable
- [ ] Buttons have sufficient contrast
- [ ] No color-only indicators

---

## Cross-Browser Testing

### Browser Versions to Test
- Chrome 120+
- Firefox 121+
- Safari 17+
- Edge 120+
- Mobile Safari (iOS 16+)
- Chrome Mobile (latest)

### Known Issues to Watch For
- [ ] YouTube iframe security restrictions
- [ ] CORS issues (shouldn't occur - YouTube handles this)
- [ ] SSL/TLS certificate warnings (shouldn't occur)

---

## Success Criteria

✅ **All Tests Passing When**:
1. All 35 recipes show unique, high-quality images
2. All 35 recipes show YouTube video embeds
3. Videos display responsively on all screen sizes
4. Video controls work correctly
5. No broken images or videos
6. Page performance is acceptable
7. Mobile and desktop both work
8. API returns proper data structures
9. No JavaScript console errors
10. Accessibility requirements met

---

## Troubleshooting

### Images Not Loading
- [ ] Check network tab in DevTools - are URLs loading?
- [ ] Verify Unsplash URLs are still valid
- [ ] Check CORS headers (shouldn't be an issue with public Unsplash)
- [ ] Try hard refresh (Ctrl+Shift+R)

### Videos Not Appearing
- [ ] Check YouTube URL format in database
- [ ] Verify `extractYouTubeId()` function is working
- [ ] Check browser console for JavaScript errors
- [ ] Verify YouTube iframe is not blocked by browser extensions
- [ ] Try different YouTube video

### Responsive Issues
- [ ] Check CSS media queries
- [ ] Verify padding/margin not causing overflow
- [ ] Test with Chrome DevTools device emulation
- [ ] Check for position: absolute elements not constraining width

---

## Performance Benchmarks

**Target Metrics**:
- Page Load Time: < 3 seconds
- Image Load Time: < 2 seconds
- Video Player Load: < 2 seconds
- Lighthouse Score: > 80 (Performance)

**Testing Tools**:
- Chrome DevTools Lighthouse
- WebPageTest.org
- Google PageSpeed Insights
- GTmetrix

---

## Regression Testing

### Existing Features Still Work
- [ ] Recipe search still works
- [ ] Trending recipes display correctly
- [ ] Recipe filters/sorting still work
- [ ] Add recipe functionality not broken
- [ ] Cook mode still works
- [ ] Ingredient substitution still works
- [ ] User authentication still works
- [ ] Admin functions still work

### Database Queries Still Fast
- [ ] Recipe listing loads quickly
- [ ] Search doesn't timeout
- [ ] Pagination works
- [ ] No N+1 queries

---

## Final Sign-Off

Once all tests pass, update this file:

- Date Tested: ___________
- Tested By: ___________
- Browser/Device: ___________
- ✅ All Tests Passed: YES / NO
- Comments: ___________
