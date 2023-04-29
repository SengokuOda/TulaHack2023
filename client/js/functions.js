//Добавление элемента на страницу
const addElement = (elem, attrs, parrent, data = "") => {
  const el = document.createElement(elem);
  const attrsArr = attrs.split(", ");
  attrsArr.forEach((attr) => {
    const [attrName, attrValue] = attr.split("=");
    el.setAttribute(attrName, attrValue.replaceAll('"', ""));
  });
  if (data.trim() !== "") {
    el.innerText = data;
  }
  parrent.appendChild(el);
};

//Найти мероприятия
const findGeo = (name) => {
  const arr = [];

  mer.forEach((geo) => {
    if (geo.geo.indexOf(name) >= 0) {
      arr.push(geo);
    }
  });

  return arr;
};

//Добавить гео точку
const addGeo = (map) => {
  mer.forEach((geo) => {
    addElement(
      "div",
      `class=search__list__item, id=${geo.id}, ontouchend=selectItem(${geo.id}), onclick=selectItem(${geo.id})`,
      list,
      geo.geo
    );
    ymaps.geocode(geo.geo).then((res) => {
      var firstGeoObject = res.geoObjects.get(0);
      var cords = firstGeoObject.geometry.getCoordinates();
      coords.push({ id: geo.id, cords });
      const newGeo = new ymaps.Placemark(
        cords,
        {
          balloonContent: geo.description,
        },
        {
          iconLayout: "default#image",
          iconImageHref: "images/самовар2.png",
          iconImageSize: [23, 25],
        }
      );
      map.geoObjects.add(newGeo);
    });
    console.log(coords);
  });
};
