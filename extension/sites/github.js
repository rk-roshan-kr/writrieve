/**
 * GitHubAdapter: Integration for GitHub Issues, PRs, and Discussions.
 */
class GitHubAdapter extends SiteAdapter {
  constructor() {
    super("github");
  }

  findComposer(container = document) {
    return container.querySelector(
      "textarea#issue_body, textarea#pull_request_body, textarea.comment-form-textarea, textarea[name='comment[body]']"
    );
  }

  getComposerWrapper(composer) {
    if (!composer) return null;
    return composer.closest(".timeline-comment, .previewable-comment-form, .js-previewable-comment-form") || composer.parentElement;
  }

  getRecipient(composer) {
    return "Repository Maintainers & Contributors";
  }

  getSubject(composer) {
    const titleInput = document.querySelector("input#issue_title, input#pull_request_title");
    return titleInput ? titleInput.value : document.title;
  }

  getExistingText(composer) {
    return composer ? (composer.value || "") : "";
  }

  getToolbar(composer) {
    const wrapper = this.getComposerWrapper(composer);
    if (!wrapper) return composer ? composer.parentElement : null;
    return wrapper.querySelector(".tabnav-tabs, .form-actions, .timeline-comment-actions") || composer.parentElement;
  }

  observeComposer(callback) {
    const visited = new WeakSet();
    const scan = () => {
      const textareas = document.querySelectorAll(
        "textarea#issue_body, textarea#pull_request_body, textarea.comment-form-textarea, textarea[name='comment[body]']"
      );
      textareas.forEach((ta) => {
        if (!visited.has(ta)) {
          visited.add(ta);
          callback(ta, this);
        }
      });
    };
    scan();
    const observer = new MutationObserver(() => scan());
    observer.observe(document.body, { childList: true, subtree: true });
  }
}

if (typeof window !== "undefined") {
  window.GitHubAdapter = GitHubAdapter;
}
