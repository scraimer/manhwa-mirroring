const tocChapterLinks = Array.from(document.querySelectorAll('.chapter-link[data-chapter]'));
const tocStoryName = window.STORY_NAME || '';
const tocHideEndpoint = window.HIDE_CHAPTER_ENDPOINT || '/cgi-bin/hide_chapter.py';

function updateTocHiddenState(hiddenChapters) {
    tocChapterLinks.forEach((link) => {
        const isHidden = hiddenChapters.has(link.dataset.chapter);
        link.classList.toggle('is-hidden', isHidden);
    });
}

async function loadTocHiddenState() {
    try {
        const params = new URLSearchParams({ story: tocStoryName });
        const response = await fetch(`${tocHideEndpoint}?${params.toString()}`, { cache: 'no-store' });
        if (!response.ok) {
            throw new Error(`Failed to load hidden chapters: ${response.status}`);
        }

        const data = await response.json();
        const hiddenChapters = new Set(
            (data.hidden || [])
                .map((item) => item.chapter)
                .filter(Boolean),
        );
        updateTocHiddenState(hiddenChapters);
    } catch (error) {
        console.error(error);
        updateTocHiddenState(new Set());
    }
}

void loadTocHiddenState();
