//上传文件
document.getElementById("fileInput").addEventListener("change", async function (event) {
  const fileList = document.getElementById("fileList");
  const files = event.target.files;

  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);

    const listItem = document.createElement("li");
    listItem.textContent = file.name;
    fileList.appendChild(listItem);
  }

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      console.log("文件上传成功:", result);

      if (result.logs) {
        result.logs.forEach((log) => {
          const logItem = document.createElement("li");
          logItem.textContent = log;
          document.querySelector(".log-list").appendChild(logItem);
        });
      }
    } else {
      console.error("文件上传失败", response.statusText);
    }
  } catch (error) {
    console.error("文件上传发生错误", error);
  }
});

// 下载所有文件
document.getElementById("downloadAllButton").addEventListener("click", async function () {
  try {
    const response = await fetch("/download", { method: "GET" });
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "files.zip"; // 打包为 ZIP 文件
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      console.log("文件下载成功");
    } else {
      console.error("文件下载失败", response.statusText);
    }
  } catch (error) {
    console.error("文件下载发生错误", error);
  }
});

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