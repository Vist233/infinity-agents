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

  document.addEventListener("DOMContentLoaded", () => {
    const bubbles = document.querySelectorAll(".bubble");

    bubbles.forEach((bubble) => {
      const markdownText = bubble.getAttribute("data-markdown");
      if (markdownText) {
        // 使用 marked.js 解析 Markdown
        bubble.innerHTML = marked(markdownText);
      }
    });
  });