const container = document.getElementById('container');
const progressBar = document.getElementById('progress');
const currentPageSpan = document.getElementById('current-page');
const topNav = document.querySelector('.top-nav');
const images = document.querySelectorAll('.manga-page');
const pageCount = window.PAGE_COUNT || 0;
const nextChapterFile = window.NEXT_CHAPTER_FILE || null;
const swipeIndicator = document.getElementById('swipeIndicator');
const swipeProgressLine = document.getElementById('swipeProgressLine');
const verticalSwipeIndicator = document.getElementById('verticalSwipeIndicator');
const verticalSwipeProgressLine = document.getElementById('verticalSwipeProgressLine');

let lastScrollY = 0;
let lastNavToggleScrollY = 0;
let imagesLoaded = false;
let isAtBottomOfPage = false;

// Touch gesture tracking
let touchStartX = 0;
let touchStartY = 0;
let touchEndX = 0;
let touchEndY = 0;
let isHorizontalSwiping = false;
let isVerticalSwiping = false;

function getChunkImages(chunkNumber) {
    return Array.from(images).filter((img) => Number(img.dataset.chunk) === chunkNumber);
}

function activateChunk(chunkImages) {
    chunkImages.forEach((img) => {
        const deferredSrc = img.getAttribute('data-src');
        if (deferredSrc) {
            img.classList.remove('deferred-page');
            img.setAttribute('src', deferredSrc);
            img.removeAttribute('data-src');
            img.loading = 'eager';
            img.decoding = 'async';
        }
    });
}

function waitForChunk(chunkImages) {
    if (chunkImages.length === 0) {
        return Promise.resolve();
    }

    return new Promise((resolve) => {
        let loadedCount = 0;
        const markLoaded = () => {
            loadedCount += 1;
            if (loadedCount === chunkImages.length) {
                resolve();
            }
        };

        chunkImages.forEach((img) => {
            if (img.complete) {
                markLoaded();
                return;
            }

            img.addEventListener('load', markLoaded, { once: true });
            img.addEventListener('error', markLoaded, { once: true });
        });
    });
}

async function initializeImageLoading() {
    if (images.length === 0) {
        imagesLoaded = true;
        return;
    }

    const firstChunk = getChunkImages(1);
    const secondChunk = getChunkImages(2);
    const thirdChunk = getChunkImages(3);

    activateChunk(firstChunk);
    await waitForChunk(firstChunk);

    activateChunk(secondChunk);
    await waitForChunk(secondChunk);

    activateChunk(thirdChunk);
    await waitForChunk(thirdChunk);

    imagesLoaded = true;
}

// Update progress bar and page counter
function updateProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = docHeight ? (scrollTop / docHeight) * 100 : 0;
    progressBar.style.width = scrollPercent + '%';
    
    // Find current page based on scroll position
    let currentPage = 1;
    images.forEach((img, index) => {
        const rect = img.getBoundingClientRect();
        if (rect.top < window.innerHeight / 2) {
            currentPage = index + 1;
        }
    });
    currentPageSpan.textContent = currentPage;
    
    // Hide/show toolbar based on scroll direction and distance
    const scrollDelta = scrollTop - lastScrollY;
    const distanceFromLastToggle = Math.abs(scrollTop - lastNavToggleScrollY);
    
    if (scrollDelta > 0 && scrollTop > 400 && distanceFromLastToggle > 100) {
        // Scrolling down and past threshold
        topNav.classList.add('hidden');
        lastNavToggleScrollY = scrollTop;
    } else if (scrollDelta < 0 && distanceFromLastToggle > 100) {
        // Scrolling up
        topNav.classList.remove('hidden');
        lastNavToggleScrollY = scrollTop;
    }
    
    lastScrollY = scrollTop;
    
    // Check if at bottom of page
    if (imagesLoaded && nextChapterFile && scrollTop > docHeight - 300) {
        isAtBottomOfPage = true;
    } else {
        isAtBottomOfPage = false;
    }
}

// Update horizontal swipe indicator position
function updateSwipeIndicator(currentX) {
    if (!isHorizontalSwiping || !nextChapterFile) return;
    
    const screenWidth = window.innerWidth;
    const distanceFromRight = screenWidth - currentX;
    const minDragDistance = screenWidth * 0.25;
    const middleOfScreen = screenWidth * 0.5;
    
    // Don't show indicator until dragged at least 25%
    if (distanceFromRight < minDragDistance) {
        swipeIndicator.classList.remove('active');
        swipeProgressLine.classList.remove('active');
        return;
    }
    
    swipeIndicator.classList.add('active');
    swipeProgressLine.classList.add('active');
    
    // Position arrow based on distance pulled
    const arrowDistance = (screenWidth - currentX) * 0.5;
    swipeIndicator.style.right = arrowDistance + 'px';
    
    // Color and scale based on threshold
    const arrow = swipeIndicator.querySelector('.swipe-arrow');
    if (distanceFromRight > middleOfScreen) {
        // Haven't reached middle yet - purple/ready state
        arrow.style.background = 'rgba(168, 85, 247, 0.3)';
        arrow.style.borderColor = 'rgba(168, 85, 247, 0.6)';
        arrow.style.color = 'rgba(168, 85, 247, 0.8)';
        arrow.style.filter = 'drop-shadow(0 0 8px rgba(168, 85, 247, 0.3))';
        arrow.style.boxShadow = 'none';
    } else {
        // Reached middle - green/caution state
        arrow.style.background = 'rgba(34, 197, 94, 0.4)';
        arrow.style.borderColor = 'rgba(34, 197, 94, 0.8)';
        arrow.style.color = '#22c55e';
        arrow.style.filter = 'drop-shadow(0 0 12px rgba(34, 197, 94, 0.8))';
        arrow.style.boxShadow = 'inset 0 0 12px rgba(34, 197, 94, 0.3)';
    }
    
    // Update progress line width
    const lineWidth = Math.min(screenWidth * 0.5, (screenWidth - currentX) * 0.5);
    swipeProgressLine.style.width = lineWidth + 'px';
}

// Handle horizontal swipe release
function handleSwipeRelease(currentX) {
    if (!isHorizontalSwiping || !nextChapterFile) return;
    
    const screenWidth = window.innerWidth;
    const distanceFromRight = screenWidth - currentX;
    const minDragDistance = screenWidth * 0.25;
    const middleOfScreen = screenWidth * 0.5;
    
    // Clear indicator
    swipeIndicator.classList.remove('active');
    swipeProgressLine.classList.remove('active');
    isHorizontalSwiping = false;
    
    // Navigate if released while purple (between 25% and 50% drag)
    if (distanceFromRight >= minDragDistance && distanceFromRight > middleOfScreen) {
        // Use same navigation method as scroll-to-bottom for consistency
        setTimeout(() => {
            window.location.href = nextChapterFile;
        }, 0);
    }
}

// Update vertical swipe indicator position
function updateVerticalSwipeIndicator(currentY) {
    if (!isVerticalSwiping || !nextChapterFile || !isAtBottomOfPage) return;
    
    const screenHeight = window.innerHeight;
    const distanceFromBottom = screenHeight - currentY;
    const minDragDistance = screenHeight * 0.15;
    const middleOfScreen = screenHeight * 0.30;
    
    // Don't show indicator until dragged at least 15%
    if (distanceFromBottom < minDragDistance) {
        verticalSwipeIndicator.classList.remove('active');
        verticalSwipeProgressLine.classList.remove('active');
        return;
    }
    
    verticalSwipeIndicator.classList.add('active');
    verticalSwipeProgressLine.classList.add('active');
    
    // Position arrow based on distance pulled
    const arrowDistance = (screenHeight - currentY) * 0.30;
    verticalSwipeIndicator.style.bottom = arrowDistance + 'px';
    
    // Color and scale based on threshold
    const arrow = verticalSwipeIndicator.querySelector('.vertical-swipe-arrow');
    if (distanceFromBottom > middleOfScreen) {
        // Haven't reached middle yet - purple/ready state
        arrow.style.background = 'rgba(168, 85, 247, 0.3)';
        arrow.style.borderColor = 'rgba(168, 85, 247, 0.6)';
        arrow.style.color = 'rgba(168, 85, 247, 0.8)';
        arrow.style.filter = 'drop-shadow(0 0 8px rgba(168, 85, 247, 0.3))';
        arrow.style.boxShadow = 'none';
    } else {
        // Reached middle - green/caution state
        arrow.style.background = 'rgba(34, 197, 94, 0.4)';
        arrow.style.borderColor = 'rgba(34, 197, 94, 0.8)';
        arrow.style.color = '#22c55e';
        arrow.style.filter = 'drop-shadow(0 0 12px rgba(34, 197, 94, 0.8))';
        arrow.style.boxShadow = 'inset 0 0 12px rgba(34, 197, 94, 0.3)';
    }
    
    // Update progress line height
    const lineHeight = Math.min(screenHeight * 0.5, (screenHeight - currentY) * 0.5);
    verticalSwipeProgressLine.style.height = lineHeight + 'px';
}

// Handle vertical swipe release
function handleVerticalSwipeRelease(currentY) {
    if (!isVerticalSwiping || !nextChapterFile || !isAtBottomOfPage) return;
    
    const screenHeight = window.innerHeight;
    const distanceFromBottom = screenHeight - currentY;
    const minDragDistance = screenHeight * 0.15;
    const middleOfScreen = screenHeight * 0.30;
    
    // Clear indicator
    verticalSwipeIndicator.classList.remove('active');
    verticalSwipeProgressLine.classList.remove('active');
    isVerticalSwiping = false;
    
    // Navigate if released while purple (between 15% and 30% drag)
    if (distanceFromBottom >= minDragDistance && distanceFromBottom > middleOfScreen) {
        setTimeout(() => {
            window.location.href = nextChapterFile;
        }, 0);
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        window.scrollBy(0, window.innerHeight * 0.8);
    } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        window.scrollBy(0, -window.innerHeight * 0.8);
    }
});

// Touch event listeners for swipe detection
document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
    
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    const distanceFromRight = screenWidth - touchStartX;
    const distanceFromBottom = screenHeight - touchStartY;
    
    // Horizontal swipe: only start if touch begins in rightmost 12%
    if (distanceFromRight < screenWidth * 0.12 && nextChapterFile) {
        isHorizontalSwiping = true;
    }
    
    // Vertical swipe: only start if at bottom of page and touch is in bottom 30%
    if (distanceFromBottom < screenHeight * 0.30 && isAtBottomOfPage && nextChapterFile) {
        isVerticalSwiping = true;
    }
}, false);

document.addEventListener('touchmove', (e) => {
    if (isHorizontalSwiping) {
        const currentX = e.changedTouches[0].screenX;
        updateSwipeIndicator(currentX);
    }
    if (isVerticalSwiping) {
        const currentY = e.changedTouches[0].screenY;
        updateVerticalSwipeIndicator(currentY);
    }
}, false);

document.addEventListener('touchend', (e) => {
    if (isHorizontalSwiping) {
        const currentX = e.changedTouches[0].screenX;
        handleSwipeRelease(currentX);
    }
    if (isVerticalSwiping) {
        const currentY = e.changedTouches[0].screenY;
        handleVerticalSwipeRelease(currentY);
    }
}, false);

window.addEventListener('scroll', updateProgress);
window.addEventListener('resize', updateProgress);

// Initialize image loading tracking
initializeImageLoading();

// Initial update
updateProgress();
