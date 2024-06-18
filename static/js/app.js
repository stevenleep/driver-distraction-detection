import { auth, httpService } from "./init.js";

const signOutButton = document.getElementById("signOutButton");
signOutButton.addEventListener("click", onSignOut);

function onSignOut() {
  auth.signOut();
  window.location.replace("/signin.html");
}

function activeFakeBtn(fakeBtnGroups, activeClassName = "") {
  fakeBtnGroups.forEach(function (fakeBtn) {
    fakeBtn.classList.remove("active");
    if (fakeBtn.classList.contains(activeClassName)) {
      fakeBtn.classList.add("active");
    }
  });
}

function querySelectorMethod(activeClassName = "") {
  const fakeBtnGroups = document.querySelectorAll(".fake-btn");
  const target = {
    isSelected: false,
    selectedMethod: "",
  };

  fakeBtnGroups.forEach(function (fakeBtn) {
    const isSelected = fakeBtn.classList.contains("active");
    const isTargetMethod = fakeBtn.classList.contains(activeClassName);
    const selectedMethod = fakeBtn.getAttribute("data-method");
    if (activeClassName && isSelected && isTargetMethod) {
      target.isSelected = true;
      target.selectedMethod = activeClassName;
    }
    if (isSelected) {
      target.isSelected = true;
      target.selectedMethod = selectedMethod;
    }
  });

  return target;
}

function initUserProfile() {
  const username = document.getElementById("username");
  const userProfile = auth.getUserProfile();
  if (userProfile) {
    username.innerText = userProfile.username;
  }
}

function activeElement(typeFakeBtns = []) {
  typeFakeBtns.forEach(function (typeFakeBtn) {
    typeFakeBtn.addEventListener("click", function () {
      const type = this.dataset.type;
      activeFakeBtn(typeFakeBtns, type);
    });
  });
}

function togglePreviewContainer(display = "none") {
  const previewContainer = document.querySelectorAll(
    ".hidden_preview_container"
  );
  previewContainer.forEach(function (container) {
    container.style.display = display;
  });
}

function previewSelectedImage(
  picture,
  previewPicture,
  previewVideo,
  fakeBtnGroups = [],
  previewResultImage
) {
  picture.addEventListener("change", function () {
    previewResultImage.setAttribute("hidden", "hidden");
    activeFakeBtn(fakeBtnGroups || [], "picture");
    previewVideo.style.display = "none";
    const file = picture.files[0];
    if (!file) {
      return;
    }
    togglePreviewContainer("block");
    const reader = new FileReader();
    reader.onload = function () {
      previewPicture.src = reader.result;
      previewPicture.style.display = "block";
    };
    reader.readAsDataURL(file);
  });
}

function previewSelectedVideo(
  video,
  previewPicture,
  previewVideo,
  fakeBtnGroups = [],
  previewResultImage
) {
  video.addEventListener("change", function () {
    previewResultImage.setAttribute("hidden", "hidden");
    activeFakeBtn(fakeBtnGroups || [], "video");
    previewPicture.style.display = "none";
    const file = video.files[0];

    if (!file) {
      return;
    }

    togglePreviewContainer("block");
    const reader = new FileReader();
    reader.onload = function () {
      previewVideo.src = reader.result;
      previewVideo.style.display = "block";
    };
    reader.readAsDataURL(file);
  });
}

document.addEventListener("DOMContentLoaded", function () {
  initUserProfile();

  const video = document.getElementById("video");
  const picture = document.getElementById("picture");
  const typeFakeBtns = document.querySelectorAll(".fake-btn.type");
  const previewVideo = document.querySelector(".preview video");
  const previewPicture = document.querySelector(".preview img");
  const fakeBtnGroups = document.querySelectorAll(".fake-btn");
  const previewResultImage = document.querySelector(".preview_result");
  const previewTitle = document.querySelector(".preview-title");

  const search = new URLSearchParams(location.search);
  const type = search.get("type");
  const md5 = search.get("md5");

  if (type && md5) {
    previewTitle.innerHTML = `正在查看结果(FileId: ${md5}) <button id="stopPreviewBtn">停止预览</button>`;
    preview(previewResultImage, { md5, type });
    stopPreview();
  } else {
    previewTitle.innerText = "检测结果";
  }

  previewSelectedImage(
    picture,
    previewPicture,
    previewVideo,
    fakeBtnGroups,
    previewResultImage
  );
  previewSelectedVideo(
    video,
    previewPicture,
    previewVideo,
    fakeBtnGroups,
    previewResultImage
  );
  handleRTC(previewResultImage);
  activeElement(typeFakeBtns);
  handleSubmit(previewResultImage);

  watchUpdate();
});

function handleSubmit(previewResultImage) {
  const form = document.querySelector("form");
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const { isSelected, selectedMethod } = querySelectorMethod();
    if (!isSelected) {
      alert("请先选择一个需要检测的内容");
      return;
    }
    previewResultImage.setAttribute("hidden", "hidden");
    previewResultImage.src = "";

    // form 的 formData 这里面包含了其他信息，我只需要选中文件的
    const formData = new FormData(form);
    const newUploadFormdata = new FormData();
    newUploadFormdata.append("type", selectedMethod);
    newUploadFormdata.append("file", formData.get(selectedMethod));
    httpService.upload(newUploadFormdata).then((result) => {
      preview(previewResultImage, result.data);
    });
  });
}

function preview(previewResultImage, previewEntity = {}) {
  previewResultImage.removeAttribute("hidden");
  previewResultImage.src = `/feed/${previewEntity.type}/${
    previewEntity.md5
  }?${new Date().getTime()}`;
}

let labelUpdateInterval;
// 实时检测
function handleRTC(previewResultImage) {
  const rtcContainer = document.querySelector(".fake-btn.rtc");
  rtcContainer.addEventListener("click", function () {
    togglePreviewContainer("none");
    previewResultImage.removeAttribute("hidden");
    previewResultImage.src = `/real_time_feed?${new Date().getTime()}`;
    // if (labelUpdateInterval) {
    //   stopWatchUpdate();
    // }
  });
}

function watchUpdate() {
  labelUpdateInterval = setInterval(fetchCurrentLabel, 1000);
}

function stopWatchUpdate() {
  labelUpdateInterval && clearInterval(labelUpdateInterval);
}

function fetchCurrentLabel() {
  const description = document.querySelector(".description");
  const predictedLabelElement = document.querySelector(".description .title");
  httpService.getLabel()
    .then((data) => {
      const label = data.label;
      if(label === "safe") {
        description.classList.remove("dangerous")
        description.classList.add("safe")
        predictedLabelElement.textContent = "🔐 安全";
      }

      if(label === "dangerous") {
        description.classList.remove("safe");
        description.classList.add("dangerous");
        predictedLabelElement.textContent = "🙅 危险"
      }
    })
    .catch((error) => console.error("Error fetching label:", error));
}

function stopPreview() {
  const stopPreviewBtn = document.querySelector("#stopPreviewBtn");
  stopPreviewBtn.addEventListener("click", () => {
    window.location.href = "index.html";
  });
}
