const path = require("path");
const { chromium } = require("playwright");

const siteUrl = process.env.SITE_URL || "http://127.0.0.1:8080/";
const outputDir = path.resolve(__dirname, "..", "..");

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath:
      process.env.EDGE_PATH ||
      "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  const errors = [];
  const failedRequests = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("requestfailed", (request) => {
    failedRequests.push(
      `${request.url()} :: ${request.failure()?.errorText || "unknown error"}`,
    );
  });

  const response = await page.goto(siteUrl, { waitUntil: "networkidle" });
  const referencePhotos = page.locator(".reference-photo");
  for (let index = 0; index < (await referencePhotos.count()); index += 1) {
    await referencePhotos.nth(index).scrollIntoViewIfNeeded();
  }
  const desktop = await page.evaluate(async () => {
    const figures = [...document.querySelectorAll(".reference-photo")];
    const images = figures.map((figure) => figure.querySelector("img"));
    await Promise.all(images.map((image) => image.decode()));
    return {
      version: document.documentElement.dataset.version,
      categories: figures.map((figure) => figure.dataset.referenceCategory),
      captions: figures.filter((figure) => figure.querySelector("figcaption"))
        .length,
      photos: images.map((image) => ({
        src: image.getAttribute("src"),
        width: image.naturalWidth,
        height: image.naturalHeight,
        alt: image.alt,
      })),
    };
  });

  await page.locator("#water .reference-photo").screenshot({
    path: path.join(outputDir, "v3.2.0-reference-photos-water.png"),
  });
  await page.locator("#signaling .reference-photo").screenshot({
    path: path.join(outputDir, "v3.2.0-reference-photos-signaling.png"),
  });
  await page.locator("#vehicle .reference-photo").screenshot({
    path: path.join(outputDir, "v3.2.0-reference-photos-vehicle.png"),
  });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload({ waitUntil: "networkidle" });
  const mobilePhotos = page.locator(".reference-photo");
  for (let index = 0; index < (await mobilePhotos.count()); index += 1) {
    await mobilePhotos.nth(index).scrollIntoViewIfNeeded();
  }
  const mobile = await page.evaluate(async () => {
    const images = [...document.querySelectorAll(".reference-photo img")];
    await Promise.all(images.map((image) => image.decode()));
    const photo = document.querySelector("#firstaid .reference-photo");
    return {
      loaded: images.filter(
        (image) => image.complete && image.naturalWidth > 0,
      ).length,
      viewportWidth: document.documentElement.clientWidth,
      documentWidth: document.documentElement.scrollWidth,
      photoWidth: photo.getBoundingClientRect().width,
    };
  });
  await page.locator("#firstaid .reference-photo").screenshot({
    path: path.join(outputDir, "v3.2.0-reference-photos-mobile.png"),
  });

  await browser.close();

  const expectedCategories = [
    "water",
    "fire",
    "shelter",
    "navigation",
    "firstaid",
    "signaling",
    "weather",
    "vehicle",
  ];
  const passed =
    response?.status() === 200 &&
    desktop.version === "3.2.0" &&
    JSON.stringify(desktop.categories) === JSON.stringify(expectedCategories) &&
    desktop.captions === expectedCategories.length &&
    desktop.photos.every(
      (photo) =>
        photo.src.startsWith("assets/references/") &&
        photo.width > 0 &&
        photo.alt,
    ) &&
    mobile.loaded === expectedCategories.length &&
    mobile.documentWidth === mobile.viewportWidth &&
    mobile.photoWidth <= mobile.viewportWidth &&
    errors.length === 0 &&
    failedRequests.length === 0;

  console.log(
    JSON.stringify(
      {
        passed,
        httpStatus: response?.status(),
        desktop,
        mobile,
        errors,
        failedRequests,
      },
      null,
      2,
    ),
  );
  if (!passed) process.exitCode = 1;
})();
