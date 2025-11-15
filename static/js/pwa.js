// PWA Registration Script
(function() {
  'use strict';

  // Проверка поддержки Service Worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      registerServiceWorker();
    });
  }

  // Регистрация Service Worker
  function registerServiceWorker() {
    navigator.serviceWorker
      .register('/static/service-worker.js')
      .then((registration) => {
        console.log('[PWA] Service Worker registered:', registration.scope);

        // Проверка обновлений
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          console.log('[PWA] New Service Worker found');

          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // Новый Service Worker готов, можно показать уведомление
              console.log('[PWA] New version available!');
              showUpdateNotification();
            }
          });
        });
      })
      .catch((error) => {
        console.error('[PWA] Service Worker registration failed:', error);
      });

    // Обработка обновлений
    let refreshing = false;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (!refreshing) {
        refreshing = true;
        console.log('[PWA] Reloading page for update...');
        window.location.reload();
      }
    });
  }

  // Показ уведомления об обновлении
  function showUpdateNotification() {
    // Можно добавить визуальное уведомление пользователю
    // Например, показать кнопку "Обновить приложение"
    const updateBanner = document.createElement('div');
    updateBanner.id = 'pwa-update-banner';
    updateBanner.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: var(--accent, #ff6b35);
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      z-index: 10000;
      display: flex;
      align-items: center;
      gap: 1rem;
      font-family: var(--font-heading, sans-serif);
      font-size: 0.9rem;
    `;
    updateBanner.innerHTML = `
      <span>Доступна новая версия приложения</span>
      <button id="pwa-update-btn" style="
        background: white;
        color: var(--accent, #ff6b35);
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.85rem;
      ">Обновить</button>
    `;

    document.body.appendChild(updateBanner);

    document.getElementById('pwa-update-btn').addEventListener('click', () => {
      if (navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
      }
      updateBanner.remove();
    });

    // Автоматически скрыть через 10 секунд
    setTimeout(() => {
      if (updateBanner.parentNode) {
        updateBanner.remove();
      }
    }, 10000);
  }

  // Обработка установки PWA
  let deferredPrompt;
  window.addEventListener('beforeinstallprompt', (e) => {
    console.log('[PWA] Install prompt available');
    e.preventDefault();
    deferredPrompt = e;

    // Показываем кнопку установки
    showInstallButton();
  });

  // Показ кнопки установки
  function showInstallButton() {
    // Проверяем, не установлено ли уже приложение
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return; // Уже установлено
    }

    const installButton = document.createElement('button');
    installButton.id = 'pwa-install-btn';
    installButton.innerHTML = '📱 Установить приложение';
    installButton.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: var(--accent, #ff6b35);
      color: white;
      border: none;
      padding: 0.75rem 1.25rem;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      z-index: 9999;
      cursor: pointer;
      font-family: var(--font-heading, sans-serif);
      font-weight: 600;
      font-size: 0.9rem;
      display: none;
    `;

    installButton.addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log('[PWA] User choice:', outcome);
        deferredPrompt = null;
        installButton.remove();
      }
    });

    document.body.appendChild(installButton);

    // Показываем кнопку через 3 секунды после загрузки
    setTimeout(() => {
      installButton.style.display = 'block';
    }, 3000);
  }

  // Обработка успешной установки
  window.addEventListener('appinstalled', () => {
    console.log('[PWA] App installed successfully');
    deferredPrompt = null;
    const installButton = document.getElementById('pwa-install-btn');
    if (installButton) {
      installButton.remove();
    }
  });
})();

