// Render markdown when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  // Configure marked to handle line breaks correctly
  marked.setOptions({
    breaks: true, // Convert single line breaks to <br>
    gfm: true,    // Use GitHub Flavored Markdown
  });

  // Render all existing markdown content on initial load
  renderMarkdown();

  // Set up an observer to re-render markdown when new messages are added
  const messageArea = document.getElementById('messageArea');
  if (messageArea) {
    const observer = new MutationObserver(function(mutations) {
      // Check if nodes were added before re-rendering
      let nodesAdded = false;
      mutations.forEach(mutation => {
        if (mutation.addedNodes.length > 0) {
          nodesAdded = true;
        }
      });
      if (nodesAdded) {
        renderMarkdown(); // Re-render markdown for new messages
      }
    });

    // Observe changes in the message area's children
    observer.observe(messageArea, { childList: true, subtree: true });
  }
});

// Function to find and render markdown in all .markdown-content elements
function renderMarkdown() {
  const markdownElements = document.querySelectorAll('.markdown-content');
  markdownElements.forEach(element => {
    // Avoid re-rendering if already done (simple check)
    if (!element.dataset.rendered) {
      const originalText = element.textContent || element.innerText; // Get raw text
      const renderedHTML = marked.parse(originalText); // Use marked.parse()
      element.innerHTML = renderedHTML; // Set the innerHTML to the rendered content
      element.dataset.rendered = 'true'; // Mark as rendered
    }
  });
}