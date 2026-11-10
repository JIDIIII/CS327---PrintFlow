(function () {
    function revealPage() {
        document.documentElement.classList.add("page-ready");
        document.documentElement.classList.remove("js-loading");
        document.querySelectorAll("[data-skeleton]").forEach(function (skeleton) {
            skeleton.remove();
        });
        var themeColor = document.querySelector('meta[name="theme-color"]');
        if (themeColor) {
            themeColor.content = document.documentElement.dataset.theme === "dark" ? "#0f172a" : "#f8fafc";
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", revealPage, { once: true });
    } else {
        revealPage();
    }
}());
