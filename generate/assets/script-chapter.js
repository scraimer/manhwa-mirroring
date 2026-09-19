const container = document.getElementById('container');
const progressBar = document.getElementById('progress');
const currentPageSpan = document.getElementById('current-page');
const topNav = document.querySelector('.top-nav');
const bottomNav = document.querySelector('.bottom-nav');
const images = document.querySelectorAll('.manga-page');
const pageCount = window.PAGE_COUNT || 0;
const chapterOrder = Array.isArray(window.CHAPTERS) ? window.CHAPTERS : [];
const currentStory = window.STORY_NAME || '';
const currentChapter = window.CURRENT_CHAPTER || null;
const hideChapterEndpoint = window.HIDE_CHAPTER_ENDPOINT || '/cgi-bin/hide_chapter.py';
const lastPageEndpoint = window.LAST_PAGE_ENDPOINT || '/cgi-bin/last_page.py';
const swipeIndicator = document.getElementById('swipeIndicator');
const swipeProgressLine = document.getElementById('swipeProgressLine');
const verticalSwipeIndicator = document.getElementById('verticalSwipeIndicator');
const verticalSwipeProgressLine = document.getElementById('verticalSwipeProgressLine');
const nextChapterDropzone = document.getElementById('nextChapterDropzone');
const navLinks = Array.from(document.querySelectorAll('[data-nav]'));
const editModeButtons = Array.from(document.querySelectorAll('[data-action="edit-mode-toggle"]'));
const hideChapterButtons = Array.from(document.querySelectorAll('[data-action="hide-chapter-toggle"]'));
const pageSelectButtons = Array.from(document.querySelectorAll('[data-action="toggle-last-page"]'));

let lastScrollY = 0;
let lastNavToggleScrollY = 0;
let imagesLoaded = false;
let hiddenChapters = new Set();
let editModeEnabled = false;
let lastPageValue = null;

// Touch gesture tracking
let touchStartX = 0;
let touchStartY = 0;
let touchEndX = 0;
let touchEndY = 0;
let isHorizontalSwiping = false;
let isVerticalSwiping = false;

function getChapterIndex(chapterFolder) {
    return chapterOrder.findIndex((chapter) => chapter.folder === chapterFolder);
}

function getVisibleNeighbor(chapterFolder, direction) {
    const currentIndex = getChapterIndex(chapterFolder);
    if (currentIndex === -1) {
        return null;
    }

    const step = direction === 'prev' ? -1 : 1;
    for (let index = currentIndex + step; index >= 0 && index < chapterOrder.length; index += step) {
        const chapter = chapterOrder[index];
        if (!hiddenChapters.has(chapter.folder)) {
            return chapter;
        }
    }

    return null;
}

function getCurrentHiddenState() {
    return currentChapter ? hiddenChapters.has(currentChapter) : false;
}

function setNavElementState(element, target) {
    if (!element) {
        return;
    }

    if (target) {
        if (element.tagName === 'A') {
            element.href = target.file;
        }
        element.setAttribute('aria-disabled', 'false');
        element.classList.remove('is-disabled');
        if ('disabled' in element) {
            element.disabled = false;
        }
    } else {
        if (element.tagName === 'A') {
            element.setAttribute('href', '#');
        }
        element.setAttribute('aria-disabled', 'true');
        element.classList.add('is-disabled');
        if ('disabled' in element) {
            element.disabled = true;
        }
    }
}

function updateNavigationLinks() {
    const prevTarget = currentChapter ? getVisibleNeighbor(currentChapter, 'prev') : null;
    const nextTarget = currentChapter ? getVisibleNeighbor(currentChapter, 'next') : null;

    navLinks.forEach((element) => {
        if (element.dataset.nav === 'prev') {
            setNavElementState(element, prevTarget);
            if (prevTarget && element.dataset.fallbackHref) {
                element.href = prevTarget.file;
            }
        } else if (element.dataset.nav === 'next') {
            setNavElementState(element, nextTarget);
            if (nextTarget && element.dataset.fallbackHref) {
                element.href = nextTarget.file;
            }
        }
    });
}

function updateEditModeUi() {
    document.body.classList.toggle('edit-mode', editModeEnabled);
    if (topNav) {
        topNav.classList.toggle('edit-mode', editModeEnabled);
    }
    if (bottomNav) {
        bottomNav.classList.toggle('edit-mode', editModeEnabled);
    }

    editModeButtons.forEach((button) => {
        button.textContent = editModeEnabled ? 'Exit Edit Mode' : 'Edit Mode';
    });

    hideChapterButtons.forEach((button) => {
        button.style.display = editModeEnabled ? 'inline-flex' : '';
    });
}

function updateHideChapterButtons() {
    const isHidden = getCurrentHiddenState();
    hideChapterButtons.forEach((button) => {
        button.textContent = isHidden ? 'Unhide Chapter' : 'Hide Chapter';
    });

    document.body.classList.toggle('current-chapter-hidden', isHidden);
}

function refreshAllState() {
    updateNavigationLinks();
    updateEditModeUi();
    updateHideChapterButtons();
    updatePageVisibility();
}

function updatePageVisibility() {
    images.forEach((img) => {
        const pageNumber = Number(img.dataset.page);
        const container = img.closest('.page-container');
        if (!container) {
            return;
        }
        const isBeyondLastPage = lastPageValue !== null && pageNumber > lastPageValue;
        container.classList.toggle('beyond-last-page', isBeyondLastPage);
    });

    pageSelectButtons.forEach((button) => {
        const pageNumber = Number(button.dataset.page);
        const isCurrentLastPage = lastPageValue === pageNumber;
        button.classList.toggle('is-last-page', isCurrentLastPage);
        button.textContent = isCurrentLastPage ? 'Unset Last Page' : 'Set as Last Page';
    });
}

async function loadLastPage() {
    if (!currentChapter) {
        return;
    }

    try {
        const params = new URLSearchParams({ story: currentStory, chapter: currentChapter });
        const response = await fetch(`${lastPageEndpoint}?${params.toString()}`, { cache: 'no-store' });
        if (!response.ok) {
            throw new Error(`Failed to load last page: ${response.status}`);
        }

        const data = await response.json();
        lastPageValue = typeof data.last_page === 'number' ? data.last_page : null;
    } catch (error) {
        console.error(error);
        lastPageValue = null;
    } finally {
        updatePageVisibility();
    }
}

async function toggleLastPage(pageNumber) {
    if (!currentChapter) {
        return;
    }

    const form = new URLSearchParams();
    form.set('story', currentStory);
    form.set('chapter', currentChapter);
    form.set('page', String(pageNumber));

    const response = await fetch(lastPageEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        },
        body: form.toString(),
    });

    if (!response.ok) {
        throw new Error(`Failed to update last page: ${response.status}`);
    }

    const data = await response.json();
    if (!data.ok) {
        throw new Error('Failed to update last page');
    }

    lastPageValue = typeof data.last_page === 'number' ? data.last_page : null;
    updatePageVisibility();
}

function getChapterEndpointForm(hidden) {
    const form = new URLSearchParams();
    form.set('story', currentStory || '');
    form.set('chapter', currentChapter || '');
    form.set('hidden', hidden ? '1' : '0');
    return form;
}

async function loadHiddenChapters() {
    try {
        const params = new URLSearchParams({ story: currentStory });
        const response = await fetch(`${hideChapterEndpoint}?${params.toString()}`, { cache: 'no-store' });
        if (!response.ok) {
            throw new Error(`Failed to load hidden chapters: ${response.status}`);
        }

        const data = await response.json();
        hiddenChapters = new Set(
            (data.hidden || [])
                .map((item) => item.chapter)
                .filter(Boolean),
        );
    } catch (error) {
        console.error(error);
        hiddenChapters = new Set();
    } finally {
        refreshAllState();
    }
}

async function toggleCurrentChapterHidden() {
    if (!currentChapter) {
        return;
    }

    const nextHiddenState = !getCurrentHiddenState();
    const response = await fetch(hideChapterEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        },
        body: getChapterEndpointForm(nextHiddenState).toString(),
    });

    if (!response.ok) {
        throw new Error(`Failed to update hidden state: ${response.status}`);
    }

    const data = await response.json();
    if (!data.ok) {
        throw new Error('Failed to update hidden state');
    }

    if (nextHiddenState) {
        hiddenChapters.add(currentChapter);
    } else {
        hiddenChapters.delete(currentChapter);
    }

    refreshAllState();
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

function getChunkImages(chunkNumber) {
    return Array.from(images).filter((img) => Number(img.dataset.chunk) === chunkNumber);
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
        topNav.classList.add('hidden');
        lastNavToggleScrollY = scrollTop;
    } else if (scrollDelta < 0 && distanceFromLastToggle > 100) {
        topNav.classList.remove('hidden');
        lastNavToggleScrollY = scrollTop;
    }

    lastScrollY = scrollTop;
}

// Update horizontal swipe indicator position
function updateSwipeIndicator(currentX) {
    const nextTarget = currentChapter ? getVisibleNeighbor(currentChapter, 'next') : null;
    if (!isHorizontalSwiping || !nextTarget) return;

    const screenWidth = window.innerWidth;
    const distanceFromRight = screenWidth - currentX;
    const minDragDistance = screenWidth * 0.25;
    const middleOfScreen = screenWidth * 0.5;

    if (distanceFromRight < minDragDistance) {
        swipeIndicator.classList.remove('active');
        swipeProgressLine.classList.remove('active');
        return;
    }

    swipeIndicator.classList.add('active');
    swipeProgressLine.classList.add('active');

    const arrowDistance = (screenWidth - currentX) * 0.5;
    swipeIndicator.style.right = arrowDistance + 'px';

    const arrow = swipeIndicator.querySelector('.swipe-arrow');
    if (distanceFromRight > middleOfScreen) {
        arrow.style.background = 'rgba(168, 85, 247, 0.3)';
        arrow.style.borderColor = 'rgba(168, 85, 247, 0.6)';
        arrow.style.color = 'rgba(168, 85, 247, 0.8)';
        arrow.style.filter = 'drop-shadow(0 0 8px rgba(168, 85, 247, 0.3))';
        arrow.style.boxShadow = 'none';
    } else {
        arrow.style.background = 'rgba(34, 197, 94, 0.4)';
        arrow.style.borderColor = 'rgba(34, 197, 94, 0.8)';
        arrow.style.color = '#22c55e';
        arrow.style.filter = 'drop-shadow(0 0 12px rgba(34, 197, 94, 0.8))';
        arrow.style.boxShadow = 'inset 0 0 12px rgba(34, 197, 94, 0.3)';
    }

    const lineWidth = Math.min(screenWidth * 0.5, (screenWidth - currentX) * 0.5);
    swipeProgressLine.style.width = lineWidth + 'px';
}

// Handle horizontal swipe release
function handleSwipeRelease(currentX) {
    const nextTarget = currentChapter ? getVisibleNeighbor(currentChapter, 'next') : null;
    if (!isHorizontalSwiping || !nextTarget) return;

    const screenWidth = window.innerWidth;
    const distanceFromRight = screenWidth - currentX;
    const minDragDistance = screenWidth * 0.25;
    const middleOfScreen = screenWidth * 0.5;

    swipeIndicator.classList.remove('active');
    swipeProgressLine.classList.remove('active');
    isHorizontalSwiping = false;

    if (distanceFromRight >= minDragDistance && distanceFromRight > middleOfScreen) {
        setTimeout(() => {
            window.location.href = nextTarget.file;
        }, 0);
    }
}

// Update vertical swipe indicator position
function updateVerticalSwipeIndicator(currentY) {
    const nextTarget = currentChapter ? getVisibleNeighbor(currentChapter, 'next') : null;
    if (!isVerticalSwiping || !nextTarget) return;

    const screenHeight = window.innerHeight;
    const distanceFromBottom = screenHeight - currentY;
    const minDragDistance = screenHeight * 0.15;
    const middleOfScreen = screenHeight * 0.30;

    if (distanceFromBottom < minDragDistance) {
        verticalSwipeIndicator.classList.remove('active');
        verticalSwipeProgressLine.classList.remove('active');
        return;
    }

    verticalSwipeIndicator.classList.add('active');
    verticalSwipeProgressLine.classList.add('active');

    const arrowDistance = (screenHeight - currentY) * 0.30;
    verticalSwipeIndicator.style.bottom = arrowDistance + 'px';

    const arrow = verticalSwipeIndicator.querySelector('.vertical-swipe-arrow');
    if (distanceFromBottom > middleOfScreen) {
        arrow.style.background = 'rgba(168, 85, 247, 0.3)';
        arrow.style.borderColor = 'rgba(168, 85, 247, 0.6)';
        arrow.style.color = 'rgba(168, 85, 247, 0.8)';
        arrow.style.filter = 'drop-shadow(0 0 8px rgba(168, 85, 247, 0.3))';
        arrow.style.boxShadow = 'none';
    } else {
        arrow.style.background = 'rgba(34, 197, 94, 0.4)';
        arrow.style.borderColor = 'rgba(34, 197, 94, 0.8)';
        arrow.style.color = '#22c55e';
        arrow.style.filter = 'drop-shadow(0 0 12px rgba(34, 197, 94, 0.8))';
        arrow.style.boxShadow = 'inset 0 0 12px rgba(34, 197, 94, 0.3)';
    }

    const lineHeight = Math.min(screenHeight * 0.5, (screenHeight - currentY) * 0.5);
    verticalSwipeProgressLine.style.height = lineHeight + 'px';
}

// Handle vertical swipe release
function handleVerticalSwipeRelease(currentY) {
    const nextTarget = currentChapter ? getVisibleNeighbor(currentChapter, 'next') : null;
    if (!isVerticalSwiping || !nextTarget) return;

    const screenHeight = window.innerHeight;
    const distanceFromBottom = screenHeight - currentY;
    const minDragDistance = screenHeight * 0.15;
    const middleOfScreen = screenHeight * 0.30;

    verticalSwipeIndicator.classList.remove('active');
    verticalSwipeProgressLine.classList.remove('active');
    isVerticalSwiping = false;

    if (distanceFromBottom >= minDragDistance && distanceFromBottom > middleOfScreen) {
        setTimeout(() => {
            window.location.href = nextTarget.file;
        }, 0);
    }
}

navLinks.forEach((element) => {
    element.addEventListener('click', (event) => {
        if (element.getAttribute('aria-disabled') === 'true') {
            event.preventDefault();
        }
    });
});

navLinks.forEach((element) => {
    setNavElementState(element, null);
});

editModeButtons.forEach((button) => {
    button.addEventListener('click', () => {
        editModeEnabled = !editModeEnabled;
        updateEditModeUi();
        updateHideChapterButtons();
    });
});

hideChapterButtons.forEach((button) => {
    button.addEventListener('click', async () => {
        try {
            button.disabled = true;
            await toggleCurrentChapterHidden();
        } catch (error) {
            console.error(error);
        } finally {
            button.disabled = false;
        }
    });
});

pageSelectButtons.forEach((button) => {
    button.addEventListener('click', async () => {
        const pageNumber = Number(button.dataset.page);
        try {
            button.disabled = true;
            await toggleLastPage(pageNumber);
        } catch (error) {
            console.error(error);
        } finally {
            button.disabled = false;
        }
    });
});

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
    const distanceFromRight = screenWidth - touchStartX;

    if (distanceFromRight < screenWidth * 0.12 && currentChapter && getVisibleNeighbor(currentChapter, 'next')) {
        isHorizontalSwiping = true;
    }

    if (nextChapterDropzone && currentChapter && getVisibleNeighbor(currentChapter, 'next')) {
        const dropzoneRect = nextChapterDropzone.getBoundingClientRect();
        const touchStartsInDropzone = touchStartY >= dropzoneRect.top && touchStartY <= dropzoneRect.bottom
            && touchStartX >= dropzoneRect.left && touchStartX <= dropzoneRect.right;
        if (touchStartsInDropzone) {
            isVerticalSwiping = true;
        }
    }
}, false);

document.addEventListener('touchmove', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    touchEndY = e.changedTouches[0].screenY;

    if (isHorizontalSwiping) {
        updateSwipeIndicator(touchEndX);
    }
    if (isVerticalSwiping) {
        updateVerticalSwipeIndicator(touchEndY);
    }
}, false);

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    touchEndY = e.changedTouches[0].screenY;

    if (isHorizontalSwiping) {
        handleSwipeRelease(touchEndX);
    }
    if (isVerticalSwiping) {
        handleVerticalSwipeRelease(touchEndY);
    }
}, false);

window.addEventListener('scroll', updateProgress);
window.addEventListener('resize', updateProgress);

void loadHiddenChapters();
void loadLastPage();
void initializeImageLoading();
updateProgress();
