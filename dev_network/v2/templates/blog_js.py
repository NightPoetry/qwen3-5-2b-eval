"""博客JS模板 — 导航切换+渐入动画。"""


def generate() -> str:
    return """document.addEventListener('DOMContentLoaded', () => {
  const items = document.querySelectorAll('.nav-item');
  const sections = document.querySelectorAll('.section');

  items.forEach(item => {
    item.addEventListener('click', e => {
      e.preventDefault();
      const id = item.dataset.section;

      items.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      sections.forEach(s => {
        s.classList.remove('active');
        if (s.id === id) {
          s.classList.add('active');
          s.querySelectorAll('[style*="--i"]').forEach((el, i) => {
            el.style.animation = 'none';
            el.offsetHeight;
            el.style.animation = '';
            el.style.setProperty('--i', i * 0.06 + 's');
          });
        }
      });
    });
  });
});
"""
