"use strict";

(() => {
  const media = document.getElementById("article-media");
  if (!media?.dataset.articleId) return;
  const status = document.getElementById("media-status");
  let picker;

  function insertImage(url, target) {
    const field = document.getElementById(target);
    if (!field || !url.startsWith("/") || url.startsWith("//")) return;
    if (target === "main_image") {
      field.value = url;
    } else if (target === "textbody") {
      const image = document.createElement("img");
      image.src = url;
      image.alt = "";
      field.setRangeText(image.outerHTML, field.selectionStart, field.selectionEnd, "end");
    }
    field.dispatchEvent(new Event("input", { bubbles: true }));
  }

  for (const target of ["main_image", "textbody"]) {
    const field = document.getElementById(target);
    if (!field) continue;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-secondary btn-sm mt-2";
    button.textContent = "Вибрати зображення";
    button.addEventListener("click", () => {
      picker = window.open(`${media.dataset.browseUrl}?target=${target}`, "media-picker", "width=760,height=600");
    });
    field.insertAdjacentElement("afterend", button);
  }

  window.addEventListener("message", (event) => {
    if (event.origin !== window.location.origin || event.source !== picker) return;
    if (event.data?.type === "media-selected" && typeof event.data.url === "string") {
      insertImage(event.data.url, event.data.target);
    }
  });

  const upload = document.createElement("input");
  upload.type = "file";
  upload.accept = "image/png,image/jpeg,image/gif,image/webp";
  upload.setAttribute("aria-label", "Завантажити зображення до статті");
  upload.addEventListener("change", async () => {
    if (!upload.files.length) return;
    upload.disabled = true;
    status.textContent = "Завантаження…";
    const data = new FormData();
    data.append("upload", upload.files[0]);
    try {
      const response = await fetch(media.dataset.uploadUrl, {
        method: "POST", body: data, headers: { "X-CSRFToken": media.dataset.csrf },
      });
      const result = await response.json();
      if (!response.ok || !result.uploaded) throw new Error(result.error?.message || "Не вдалося завантажити зображення.");
      insertImage(result.url, "textbody");
      status.textContent = "Зображення завантажено й додано до тексту. Збережіть статтю.";
    } catch (error) {
      status.textContent = error.message;
    } finally {
      upload.disabled = false;
      upload.value = "";
    }
  });
  media.prepend(upload);
})();
