document.addEventListener('DOMContentLoaded', function () {
  const regionDictScript = document.getElementById('region-dict');
  let regionDict = {};

  if (regionDictScript) {
    try {
      regionDict = JSON.parse(regionDictScript.textContent);
    } catch (e) {
      console.error('Ошибка парсинга region-dict:', e);
    }
  }

  const regionTextEl = document.getElementById('regionText');
  const regionBannerEl = document.getElementById('regionBanner');
  const acceptBtn = document.getElementById('acceptRegionBtn');
  const declineBtn = document.getElementById('declineRegionBtn');

  if (regionBannerEl) {
    regionBannerEl.style.display = 'block';
  }

  if (regionTextEl) {
    regionTextEl.textContent = 'ваш регион'; 
  }

  fetch('http://ip-api.com/json/')
    .then(response => {
      if (!response.ok) throw new Error('Сеть: ' + response.status);
      return response.json();
    })
    .then(data => {
      if (data.status === 'success' && data.regionName) {
        const regionEn = data.regionName;
        const regionRu = regionDict[regionEn] || regionEn;

        if (regionTextEl) {
          regionTextEl.textContent = regionRu;
        }
      }
    })
    .catch(error => {
      console.warn('Геолокация не удалась, баннер остался:', error);
    });

  if (acceptBtn) {
    acceptBtn.addEventListener('click', function () {
      if (regionBannerEl) {
        regionBannerEl.style.display = 'none';
      }
      const regionField = document.querySelector('[name="region"]');
      if (regionField && regionTextEl) {
        regionField.value = regionTextEl.textContent;
      }
      localStorage.setItem('userRegionConfirmed', 'true');
    });
  }

  if (declineBtn) {
    declineBtn.addEventListener('click', function () {
      if (regionBannerEl) {
        regionBannerEl.style.display = 'none';
      }
      localStorage.setItem('userRegionConfirmed', 'false');
    });
  }
});