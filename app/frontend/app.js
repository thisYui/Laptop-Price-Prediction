const fields = [
  "brand",
  "model",
  "ram_gb",
  "storage_gb",
  "storage_type",
  "screen_size_inch",
  "cpu_text",
  "cpu_brand",
  "cpu_family",
  "cpu_generation",
  "cpu_suffix",
  "gpu_text",
  "condition",
  "warranty_status",
];

const example = {
  description:
    "Dell Inspiron 15, Intel Core i5-1235U, RAM 16GB, SSD 512GB, màn 15.6 inch, card Intel Integrated, đã sử dụng chưa sửa chữa, hết bảo hành",
  raw_features: {
    brand: "Dell",
    model: "Inspiron",
    ram_gb: 16,
    storage_gb: 512,
    storage_type: "SSD",
    screen_size_inch: 15.6,
    cpu_text: "Intel Core i5-1235U",
    cpu_brand: "Intel",
    cpu_family: "Intel Core i5",
    cpu_generation: 12,
    cpu_suffix: "U",
    gpu_text: "Intel Integrated",
    condition: "good",
    warranty_status: "expired",
  },
};

const form = document.querySelector("#predictForm");
const runState = document.querySelector("#runState");
const predictedPrice = document.querySelector("#predictedPrice");
const validationList = document.querySelector("#validationList");
const activeFeatures = document.querySelector("#activeFeatures");
const rawJson = document.querySelector("#rawJson");
const encodedJson = document.querySelector("#encodedJson");
const healthStatus = document.querySelector("#healthStatus");
const healthDetail = document.querySelector("#healthDetail");
const inputPanel = document.querySelector(".input-panel");

function getMode() {
  return document.querySelector('input[name="mode"]:checked')?.value || "text";
}

function syncModeVisibility() {
  inputPanel.dataset.mode = getMode();
}

function nullableValue(id) {
  const element = document.querySelector(`#${id}`);
  const value = element.value.trim();
  if (!value) return null;
  if (["ram_gb", "storage_gb", "screen_size_inch"].includes(id)) return Number(value);
  if (id === "cpu_generation") return Number.parseInt(value, 10);
  return value;
}

function collectRawFeatures() {
  return Object.fromEntries(fields.map((field) => [field, nullableValue(field)]));
}

function setJson(element, value) {
  element.textContent = JSON.stringify(value, null, 2);
}

function setValidation(items) {
  validationList.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    validationList.appendChild(li);
  });
}

function setChips(items) {
  activeFeatures.innerHTML = "";
  if (!items.length) {
    activeFeatures.innerHTML = "<span>Không có feature nổi bật</span>";
    return;
  }
  items.forEach((item) => {
    const chip = document.createElement("span");
    chip.textContent = item;
    activeFeatures.appendChild(chip);
  });
}

function formatPrice(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "--";
  return value.toLocaleString("vi-VN", { maximumFractionDigits: 3 });
}

function setLoading(isLoading) {
  form.querySelector(".primary-button").disabled = isLoading;
  runState.textContent = isLoading ? "Đang chạy" : "Hoàn tất";
}

function fillExample() {
  document.querySelector("#description").value = example.description;
  fields.forEach((field) => {
    const element = document.querySelector(`#${field}`);
    element.value = example.raw_features[field] ?? "";
  });
  setJson(rawJson, example.raw_features);
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    healthStatus.textContent = data.ok ? "Sẵn sàng" : "Có lỗi";
    healthDetail.textContent = data.model_available
      ? "Model full-data đã sẵn sàng. Mode LLM dùng GEMINI_API_KEY."
      : "Không tìm thấy model full-data trong thư mục models.";
  } catch (error) {
    healthStatus.textContent = "Không kết nối";
    healthDetail.textContent = "Hãy chạy backend server trước.";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  document.querySelector(".result-panel").classList.remove("is-error");
  setLoading(true);
  setValidation(["Đang gửi dữ liệu tới backend."]);
  predictedPrice.textContent = "--";

  const mode = getMode();
  const payload =
    mode === "manual"
      ? { mode, raw_features: collectRawFeatures() }
      : { mode, description: document.querySelector("#description").value.trim() };

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Prediction failed.");

    runState.textContent = "Hoàn tất";
    predictedPrice.textContent = formatPrice(data.predicted_price);
    setValidation(data.validation || []);
    setChips(data.active_features || []);
    setJson(rawJson, data.raw_features || {});
    setJson(encodedJson, data.encoded_features || {});

    fields.forEach((field) => {
      const element = document.querySelector(`#${field}`);
      if (element && data.raw_features && data.raw_features[field] !== null) {
        element.value = data.raw_features[field];
      }
    });
  } catch (error) {
    document.querySelector(".result-panel").classList.add("is-error");
    runState.textContent = "Lỗi";
    setValidation([error.message]);
  } finally {
    form.querySelector(".primary-button").disabled = false;
  }
});

document.querySelector("#fillExample").addEventListener("click", fillExample);

document.querySelectorAll('input[name="mode"]').forEach((input) => {
  input.addEventListener("change", syncModeVisibility);
});

document.querySelector("#clearForm").addEventListener("click", () => {
  document.querySelector("#description").value = "";
  fields.forEach((field) => {
    document.querySelector(`#${field}`).value = "";
  });
  predictedPrice.textContent = "--";
  runState.textContent = "Chưa chạy";
  setValidation(["Chờ dữ liệu đầu vào."]);
  setChips([]);
  setJson(rawJson, {});
  setJson(encodedJson, {});
});

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const id = button.getAttribute("data-copy");
    await navigator.clipboard.writeText(document.querySelector(`#${id}`).textContent);
    button.textContent = "Copied";
    setTimeout(() => {
      button.textContent = "Copy";
    }, 900);
  });
});

document.querySelectorAll(".accordion-item").forEach((item) => {
  item.addEventListener("mouseenter", () => {
    document.querySelectorAll(".accordion-item").forEach((entry) => entry.classList.remove("active"));
    item.classList.add("active");
  });
});

fillExample();
syncModeVisibility();
checkHealth();

if (window.gsap && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  gsap.from(".nav-shell", {
    y: -28,
    opacity: 0,
    duration: 0.55,
    ease: "power3.out",
  });

  gsap.from(".hero-copy > *", {
    y: 24,
    opacity: 0,
    duration: 0.55,
    stagger: 0.045,
    ease: "power3.out",
  });

  gsap.from(".hero-diagram, .input-panel, .result-panel", {
    y: 24,
    opacity: 0,
    duration: 0.55,
    stagger: 0.05,
    ease: "power3.out",
  });

  if (window.ScrollTrigger) {
    gsap.registerPlugin(ScrollTrigger);
    gsap.utils.toArray(".process-card, .json-card, .accordion-item").forEach((element) => {
      gsap.from(element, {
        y: 28,
        opacity: 0,
        duration: 0.45,
        ease: "power2.out",
        scrollTrigger: {
          trigger: element,
          start: "top 92%",
          once: true,
        },
      });
    });
  }
}
