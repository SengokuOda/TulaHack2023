let myMap;
let circle;
const list = document.querySelector(".swiper-wrapper");

const deleteControls = [
  "trafficControl",
  "searchControl",
  "scaleLine",
  "typeSelector",
];

let mer;
let categories;
(async function () {
  mer = await getEvents("events");
  categories = await getEvents("categories");
})();
setTimeout(() => {
  ymaps.ready(init);
}, 300);

const coords = [];

const myMer = [];

function init() {
  const geolocationControl = new ymaps.control.GeolocationControl({
    options: {
      float: "right",
    },
  });
  const geolocation = ymaps.geolocation;
  myMap = new ymaps.Map(
    "map",
    {
      center: [55.76, 37.64], // Москва
      zoom: 10,
      controls: [geolocationControl],
    },
    {
      searchControlProvider: "yandex#search",
    }
  );
  deleteControls.forEach((control) => {
    myMap.controls.remove(control);
  });
  // addGeo(myMap, mer);
  geolocation
    .get({
      provider: "browser",
      mapStateAutoApply: true,
    })
    .then(function (result) {
      result.geoObjects.options.set("preset", "islands#redCircleIcon");

      const ourCoords = result.geoObjects;
      myMap.geoObjects.add(ourCoords);

      circle = new ymaps.Circle([ourCoords.position, 200], null, {
        fillColor: "#DB709377",
        strokeColor: "#990066",
      });

      myMap.geoObjects.add(circle);
      const c = circle.geometry._coordinates;
      coords.forEach((m) => {
        if (
          ymaps.coordSystem.geo.getDistance(c, m.cords) <
          Number(items[index].innerText)
        ) {
          myMer.push(m);
        }
      });
    });
}

const slide = document.querySelector("#slide");
const slideContainer = document.querySelector("#search");
const radius = document.querySelector("#radius");
//mobile

function selectItem(i) {
  const id = Number(i);
  coords.forEach((geo) => {
    if (geo.id === Number(id)) {
      myMap.setCenter(geo.cords);
    }
  });
}

slide.addEventListener("touchmove", (e) => {
  var touchLocation = e.targetTouches[0];
  slideContainer.style.top = touchLocation.pageY - 670 + "px";
  radius.style.top = touchLocation.pageY - 670 + "px";
  const num = slideContainer.style.top.replace("px", "");
  if (Number(num) < -250) {
    slideContainer.style.top = "-500px";
  }
});

//desctop
slide.onmousedown = (e) => {
  let coords = getCoords(slideContainer);
  var shiftY = e.pageY - coords.top;
  function moveAt(e) {
    slideContainer.style.top = e.pageY - shiftY - 610 + "px";
    radius.style.top = e.pageY - shiftY - 620 + "px";
    const num = slideContainer.style.top.replace("px", "");
    if (Number(num) < -350) {
      slideContainer.style.top = "-600px";
    }
  }

  document.onmousemove = function (e) {
    moveAt(e);
  };

  slideContainer.onmouseup = function () {
    document.onmousemove = null;
    slide.onmouseup = null;
  };
};

function getCoords(elem) {
  // кроме IE8-
  var box = elem.getBoundingClientRect();
  return {
    top: box.top + pageYOffset,
    left: box.left + pageXOffset,
  };
}

slide.ondragstart = function () {
  return false;
};
