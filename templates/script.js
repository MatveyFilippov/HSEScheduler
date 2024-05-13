const calendar = document.querySelector('.calendar');
const monthYear = document.querySelector('.month-year');
const prevMonthBtn = document.querySelector('.prev-month');
const nextMonthBtn = document.querySelector('.next-month');
const daysContainer = document.querySelector('.calendar-days');
const selectedDaysCount = document.querySelector('.selected-days-count');
const habitListContainer = document.querySelector('.habit-list-container');




// Текущая дата
let currentDate = new Date();
let currentMonth = currentDate.getMonth();
let currentYear = currentDate.getFullYear();

let currentHabit = null;
let habitDates = {};

// Список выбранных дат
let selectedDates = [];

// Создание календаря
function createCalendar(month, year) {
 // Получение первого дня месяца
const firstDay = new Date(year, month, 1);

// Получение дня недели первого дня месяца (0 - воскресенье, 6 - суббота)
const firstDayWeekDay = firstDay.getDay();

// Создание пустого массива для дней недели
const daysOfWeek = [];

// Добавление пустых элементов в массив дней недели для соответствия первому дню недели
for (let i = 0; i < firstDayWeekDay - 1; i++) {
  // Исправление: вычитание 1 из firstDayWeekDay, чтобы первый день месяца приходился на среду (среда имеет индекс 3)
  daysOfWeek.push('');
}

// Получение количества дней в месяце
const daysInMonth = new Date(year, month + 1, 0).getDate();

// Добавление дат месяца в массив дней недели
for (let i = 1; i <= daysInMonth; i++) {
  daysOfWeek.push(i);
}

  // Очистка предыдущего календаря
  daysContainer.innerHTML = '';

  // Создание элементов календаря
  for (let i = 0; i < daysOfWeek.length; i++) {
    const day = document.createElement('div');
    day.classList.add('calendar-day');

    // Установка даты для элемента
    const date = new Date(year, month, daysOfWeek[i]);

    // Добавление класса для текущей даты
    if (date.getDate() === currentDate.getDate() && date.getMonth() === currentDate.getMonth() && date.getFullYear() === currentDate.getFullYear()) {
      day.classList.add('calendar-day--current');
    }

    // Добавление класса для дат, не принадлежащих текущему месяцу
    if (date.getMonth() !== month) {
      day.classList.add('calendar-day--not-current');
    }

    // Добавление обработчика событий нажатия для выбора даты
    day.addEventListener('click', () => {
      // Проверка, была ли дата уже выбрана
      if (selectedDates.includes(date.getTime())) {
        // Если дата была выбрана, удаление ее из списка выбранных дат и обновление интерфейса
        selectedDates = selectedDates.filter(d => d !== date.getTime());
        day.classList.remove('calendar-day--selected');
      } else {
        // Если дата не была выбрана, добавление ее в список выбранных дат и обновление интерфейса
        selectedDates.push(date.getTime());
        day.classList.add('calendar-day--selected');
      }

      // Обновление количества выбранных дней
      updateSelectedDaysCount();
    });

    // Добавление даты или пустого элемента в элемент дня
    day.textContent = daysOfWeek[i];

    // Добавление элемента в контейнер дней
    daysContainer.appendChild(day);
  }
}

// Обновление отображения месяца и года
function updateMonthYear() {
  monthYear.textContent = `${months[currentMonth]} ${currentYear}`;
}


// Обновление количества выбранных дней
function updateSelectedDaysCount() {
  selectedDaysCount.textContent = `Выполнено: ${selectedDates.length} `;
  if (selectedDates.length > 5 & selectedDates.length < 15) {
    // Обновление атрибута src элемента изображения для вывода картинки для более 5 выбранных дней
    document.getElementById('image100').src = 'static/assets/vorona 1.png';

    document.getElementById('caption').textContent = 'Ты молодец! Так держать!';
  } 
  if (selectedDates.length <= 5) {
    // Обновление атрибута src элемента изображения для вывода картинки для менее 5 выбранных дней
    document.getElementById('image100').src = 'static/assets/vorona 0.png';

    document.getElementById('caption').textContent = 'Поднимаем мотивацию!';
  }
  if (selectedDates.length > 14 & selectedDates.length < 23 ) {
    // Обновление атрибута src элемента изображения для вывода картинки для более 5 выбранных дней
    document.getElementById('image100').src = 'static/assets/vorona 3.png';

    document.getElementById('caption').textContent = 'Ты слишком крут!';
  } 
  if (selectedDates.length > 22 ) {
    // Обновление атрибута src элемента изображения для вывода картинки для более 5 выбранных дней
    document.getElementById('image100').src = 'static/assets/vorona 4.png';

    document.getElementById('caption').textContent = 'Ты мой кумир!';
  } 
  }




// Переход к предыдущему месяцу
function prevMonth() {
  currentMonth--;
  if (currentMonth < 0) {
    currentMonth = 11;
    currentYear--;
  }
  createCalendar(currentMonth, currentYear);
  updateMonthYear();
}

// Переход к следующему месяцу
function nextMonth() {
  currentMonth++;
  if (currentMonth > 11) {
    currentMonth = 0;
    currentYear++;
  }
  createCalendar(currentMonth, currentYear);
  updateMonthYear();
}

// Создание массива названий месяцев
const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

// Создание календаря при загрузке страницы
createCalendar(currentMonth, currentYear);
updateMonthYear();

// Добавление обработчиков событий нажатия на кнопки перехода по месяцам
prevMonthBtn.addEventListener('click', prevMonth);
nextMonthBtn.addEventListener('click', nextMonth);




//нужное по привычкам

const habitList = document.querySelector ('.habit-list');
const habitForm = document.querySelector ('#habit-form');
const habitButtonToggle = document.querySelector('.habit-button-toggle');

let db;

// Открытие базы данных
const openDB = () => {
  return new Promise((resolve, reject) => {
    const request = window.indexedDB.open('habitsDB', 1);

    request.onsuccess = (event) => {
      db = event.target.result;
      resolve();
    };

    request.onerror = (event) => {
      reject('Не удалось открыть базу данных.');
    };

    request.onupgradeneeded = (event) => {
      const habitsStore = event.target.result.createObjectStore('habits', { keyPath: 'id', autoIncrement: true });
    };
  });
};

// Добавление записи в базу данных
const addHabit = (habit) => {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('habits', 'readwrite');
    const habitsStore = transaction.objectStore('habits');

    const request = habitsStore.add(habit);

    request.onsuccess = (event) => {
      resolve(event.target.result);
    };

    request.onerror = (event) => {
      reject('Не удалось добавить привычку.');
    };
  });
};

// Получение всех записей из базы данных
const getAllHabits = () => {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('habits', 'readonly');
    const habitsStore = transaction.objectStore('habits');

    const request = habitsStore.getAll();

    request.onsuccess = (event) => {
      resolve(event.target.result);
    };

    request.onerror = (event) => {
      reject('Не удалось получить привычки.');
    };
  });
};

// Удаление записи из базы данных
const deleteHabit = (id) => {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('habits', 'readwrite');
    const habitsStore = transaction.objectStore('habits');

    const request = habitsStore.delete(id);

    request.onsuccess = (event) => {
      resolve();
    };

    request.onerror = (event) => {
      reject('Не удалось удалить привычку.');
    };
  });
};

// Обработка события нажатия на кнопку переключения списка привычек
habitButtonToggle.addEventListener('click', () => {
  // Переключение видимости списка привычек
  habitList.classList.toggle('active');
});

// Обработка события отправки формы
habitForm.addEventListener("submit", (e) => {
  e.preventDefault();

  const habitInput = document.querySelector("input[name='habit']");

  // Получение значения из поля ввода привычки
  const newHabit = habitInput.value;

  // Добавление новой привычки
  addHabit({ name: newHabit })
    .then((id) => {
      // Создание новой кнопки для новой привычки
      const newHabitButton = document.createElement('button');
      newHabitButton.classList.add('habit-button');
      newHabitButton.textContent = newHabit;
      newHabitButton.setAttribute('data-id', id);

      // Обработка события нажатия на кнопку новой привычки
      newHabitButton.addEventListener('click', () => {
        // Выполнение каких-либо действий, связанных с новой привычкой
        console.log(`Нажата кнопка новой привычки: ${newHabit}`);
         // Получение поля ввода для новой привычки
     const habitInput = document.querySelector('input.habit-button');

     // Установка значения поля ввода в название новой привычки
     habitInput.value = newHabit;
     
     const selectedDays = selectedDaysCount[newHabit];

     // Отображение количества выбранных дней
     alert(`Для привычки "${newHabit}" выбрано ${selectedDays} дней.`);


  
     // Обновление календаря для этой привычки
     updateCalendarForHabit(newHabit, selectedDaysCount);
   
      });

      // Добавление кнопки новой привычки в список привычек
      habitList.appendChild(newHabitButton);

      // Очистка поля ввода привычки
      habitInput.value = '';
    })
    .catch((error) => {
      alert(error);
    });
});

// Открытие базы данных
openDB()
  .then(() => {
    // Получение всех привычек
    getAllHabits()
      .then((habits) => {
        habits.forEach((habit) => {
          // Создание кнопки для каждой привычки
          const habitButton = document.createElement('button');
          habitButton.classList.add('habit-button');
          habitButton.textContent = habit.name;
          habitButton.setAttribute('data-id', habit.id);

          // Обработка события нажатия на кнопку привычки
          habitButton.addEventListener('click', () => {
            // Выполнение каких-либо действий, связанных с привычкой
            console.log(`Нажата кнопка привычки: ${habit.name}`);
      const habitInput = document.querySelector('input.habit-button');

     // Установка значения поля ввода в название новой привычки
     habitInput.value = habit.name;
     
     const selectedDays = selectedDaysCount[habit.name];

     // Отображение количества выбранных дней
     alert(`Для привычки "${habit.name}" выбрано ${selectedDays} дней.`);


  
     // Обновление календаря для этой привычки
     updateCalendarForHabit(habit.name, selectedDaysCount);
          });

          // Добавление кнопки привычки в список привычек
          habitList.appendChild(habitButton);
        });
      })
      .catch((error) => {
        alert(error);
      });
  })
  .catch((error) => {
    alert(error);
  });












const habitDaysCount = {};

function updateCalendarForHabit(habit, selectedDaysCount) {
  // Очистка ранее выбранных дат
  selectedDates = [];
  daysContainer.querySelectorAll('.calendar-day--selected').forEach(day => {
    day.classList.remove('calendar-day--selected');
  });

  // Обновление количества выбранных дней
  updateSelectedDaysCount(selectedDaysCount[habit]);

  // Добавление дат выбранных дней для новой привычки
  const habitDatesForCurrentMonth = habitDates[habit];
  if (habitDatesForCurrentMonth) {
    habitDatesForCurrentMonth.forEach(date => {
      const dayElement = daysContainer.querySelector(`[data-date="${date}"]`);
      if (dayElement) {
        dayElement.classList.add('calendar-day--selected');
        selectedDates.push(date);
      }
    });
  }
}









