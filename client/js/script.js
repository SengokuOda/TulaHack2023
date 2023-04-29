let myMap;
const list = document.querySelector("#search__list");

const deleteControls = [
  "trafficControl",
  "searchControl",
  "scaleLine",
  "typeSelector",
];

const mer = [
  {
    id: 1,
    geo: "Тула, пр. Ленина, 92",
    description: "Тулгу",
  },
  {
    id: 2,
    geo: "Тула, Галкина, 237",
    description: "Квартира",
  },
  {
    id: 3,
    geo: "Тула, Центральный переулок, 18",
    description: "Октава",
  },
  {
    id: 4,
    geo: "Октябрьская улица, 2",
    description: "Музей оружия",
  },
  {
    id: 5,
    geo: "Тула, Менделеевская улица, 8",
    description: "Тульский самовар",
  },
  {
    id: 6,
    geo: "Тула, Советская улица, 96",
    description: "Тульский цирк",
  },
  {
    id: 7,
    geo: "Тула, проспект Ленина, 34А",
    description: "Театр драмы им. М. Горького",
  },
];

const coords = [];

const myMer = [];

ymaps.ready(init);

function init() {
  const geolocation = ymaps.geolocation;
  myMap = new ymaps.Map(
    "map",
    {
      center: [55.76, 37.64], // Москва
      zoom: 10,
    },
    {
      searchControlProvider: "yandex#search",
    }
  );
  deleteControls.forEach((control) => {
    myMap.controls.remove(control);
  });
  addGeo(myMap);
  console.log(coords);
  geolocation
    .get({
      provider: "browser",
      mapStateAutoApply: true,
    })
    .then(function (result) {
      result.geoObjects.options.set("preset", "islands#redCircleIcon");
      const ourCoords = result.geoObjects;
      myMap.geoObjects.add(ourCoords);

      console.log(123);

      coords.forEach((cord) => {
        console.log(123);
        ymaps.route([ourCoords, cord.cords]).done((res) => {
          console.log(res.getHumanLength());
        });
      });
    });
}

const input = document.querySelector("input");
input.addEventListener("input", () => {
  const data = input.value;
  if (data.trim() === "") {
    while (list.firstChild) {
      list.removeChild(list.firstChild);
    }
    mer.forEach((geo) => {
      addElement(
        "div",
        `class=search__list__item, id=${geo.id}, ontouchend=selectItem(${geo.id}), onclick=selectItem(${geo.id})`,
        list,
        geo.geo
      );
    });
    return;
  }
  const searchedEl = findGeo(data);
  while (list.firstChild) {
    list.removeChild(list.firstChild);
  }
  searchedEl.forEach((geo) => {
    addElement(
      "div",
      `class=search__list__item, id=${geo.id}, , ontouchend=selectItem(${geo.id}), onclick=selectItem(${geo.id})`,
      list,
      geo.geo
    );
  });
});

const slide = document.querySelector("#slide");
const slideContainer = document.querySelector("#search");

//mobile

function selectItem(i) {
  const id = Number(i);
  console.log(coords);
  coords.forEach((geo) => {
    if (geo.id === Number(id)) {
      myMap.setCenter(geo.cords);
    }
  });
}

slideContainer.addEventListener("touchmove", (e) => {
  var touchLocation = e.targetTouches[0];
  slideContainer.style.top = touchLocation.pageY - 670 + "px";
  const num = slideContainer.style.top.replace("px", "");
  console.log(num);
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
    const num = slideContainer.style.top.replace("px", "");
    console.log(num);
    if (Number(num) < -350) {
      slideContainer.style.top = "-630px";
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
