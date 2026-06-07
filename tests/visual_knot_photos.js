const path = require("path");
const { chromium } = require("playwright");

const siteUrl = process.env.SITE_URL || "http://127.0.0.1:8080/#knots";
const outputDir = path.resolve(__dirname, "..", "..");

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath:
      process.env.EDGE_PATH ||
      "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  });
  const errors = [];
  const failedRequests = [];

  const desktopPage = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  desktopPage.on("pageerror", (error) => errors.push(String(error)));
  desktopPage.on("requestfailed", (request) => {
    failedRequests.push(
      `${request.url()} :: ${request.failure()?.errorText || "unknown error"}`,
    );
  });

  const response = await desktopPage.goto(siteUrl, {
    waitUntil: "networkidle",
  });
  const desktop = await desktopPage.evaluate(async () => {
    const images = [...document.querySelectorAll(".knot-photo img")];
    await Promise.all(images.map((image) => image.decode()));
    return {
      photos: images.map((image) => ({
        src: image.getAttribute("src"),
        width: image.naturalWidth,
        height: image.naturalHeight,
        alt: image.alt,
      })),
      figures: document.querySelectorAll(".knot-photo").length,
      captions: document.querySelectorAll(".knot-photo figcaption").length,
      localSources: images.every((image) =>
        image.getAttribute("src").startsWith("assets/knots/"),
      ),
      version: document.documentElement.dataset.version,
    };
  });
  await desktopPage.locator("#knots").screenshot({
    path: path.join(outputDir, "v3.1.0-knot-photos-desktop.png"),
  });

  await desktopPage.setViewportSize({ width: 390, height: 844 });
  await desktopPage.reload({ waitUntil: "networkidle" });
  const mobile = await desktopPage.evaluate(async () => {
    const images = [...document.querySelectorAll(".knot-photo img")];
    await Promise.all(images.map((image) => image.decode()));
    const firstPhoto = document.querySelector(".knot-photo");
    return {
      photosLoaded: images.filter(
        (image) => image.complete && image.naturalWidth > 0,
      ).length,
      viewportWidth: document.documentElement.clientWidth,
      documentWidth: document.documentElement.scrollWidth,
      photoWidth: firstPhoto.getBoundingClientRect().width,
    };
  });
  await desktopPage.locator("#knots .knot-card").first().scrollIntoViewIfNeeded();
  await desktopPage.screenshot({
    path: path.join(outputDir, "v3.1.0-knot-photo-mobile.png"),
  });

  await browser.close();

  const passed =
    response?.status() === 200 &&
    desktop.figures === 4 &&
    desktop.captions === 4 &&
    desktop.localSources &&
    desktop.version === "3.1.0" &&
    desktop.photos.every((photo) => photo.width > 0) &&
    mobile.photosLoaded === 4 &&
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
