//Добавление элемента на страницу
const addElement = (data) => {
  const [date_start, time_start] = data.start_date.split("T");
  const [date_end, time_end] = data.end_date.split("T");
  const template = `
  <div class="swiper-slide">
  <div class="card">
    <div class="header" style="background-image: url(${data.img});">
      <div class="mid">
        <div class="info">
          <h1>${data.event_name}</h1>
          <div class="date">
            <img src="./images/Calendar.png" alt="картинка" />
            ${date_start} | ${time_start}-${time_end}
          </div>
        </div>
      </div>
    </div>
    <div class="body">
      <div class="mid">
        <div class="priceAndSubs">
          <div class="price">
            <span class="pr gray small">Цена</span>
            <p>
              <span class="gold big">${data.price}₽</span
              >
            </p>
          </div>
        </div>
        <div class="event">
          <div class="rating">
            <p>${data.event_name}</p>
            <div class="gold" style="font-size: 11px">
              <img src="./images/gold_locations.png" alt="" />
              Тула
              <img src="./images/start.png" alt="" />
              25 мероприятий
            </div>
          </div>
          <div class="subsribe">
            <button class="btn subBtn" id="${data.id - 1}">Подписаться</button>
          </div>
        </div>
        <div class="description">
          ${data.description}
        </div>
        <div class="mainButton">
          <button class="btn">Купить билеты</button>
        </div>
      </div>
    </div>
  </div>
</div>`;
  list.innerHTML += template;
};

//Найти мероприятия
const findGeo = (name) => {
  const arr = [];

  mer.forEach((geo) => {
    if (geo.description.indexOf(name) >= 0) {
      arr.push(geo);
    }
  });

  return arr;
};

//Добавить гео точку
const addGeo = (map, mer) => {
  mer.forEach((geo) => {
    addElement(geo);
    ymaps.geocode(geo.address).then((res) => {
      var firstGeoObject = res.geoObjects.get(0);
      var cords = firstGeoObject.geometry.getCoordinates();
      coords.push({ id: geo.id, cords });
      const newGeo = new ymaps.Placemark(
        cords,
        {
          balloonContent: geo.event_name,
        },
        {
          iconLayout: "default#image",
          iconImageHref: "images/самовар2.png",
          iconImageSize: [23, 25],
        }
      );

      newGeo.events.add("click", function () {
        alert("О, событие!");
      });

      map.geoObjects.add(newGeo);
    });
  });
};
