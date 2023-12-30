import { For, createSignal } from "solid-js";
import { VsArrowLeft, VsArrowRight } from 'solid-icons/vs'

interface Event {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second: number;
  title: string;
  content: string;
}

const events: Event[] = [
  {"year": 2023, "month": 12, "day": 30, "hour": 12, "minute": 0, "second": 0, "title": "test", "content": "test"}
];

function getColor(cont: string) {
  if (cont == "일") {
    return "text-red-500";
  } else if (cont == "토") {
    return "text-blue-500";
  } else {
    return "text-black";
  }
}

function dayDisplay(cont: string) {
  return (
  <div class="font-normal h-full flex" style="width: calc(100vw / 7);"> 
    <div class={`mt-auto mb-auto text-center w-full font-semibold ${getColor(cont)}`}>{cont}</div>
  </div>
  );
}

function getDateList(date: Date) {
  const lastDate = new Date(date.getFullYear(), date.getMonth(), 0).getDate();
  const dateList = [];
  for (let i = 1; i <= lastDate; i++) {
    dateList.push(i);
  }
  return dateList;
}

function daySingle(num: number | undefined = undefined, today: boolean = false, events: Event[] | undefined = []) {
  if (events === undefined) {events = [];}
  let cont: string | number;
  if (num === undefined) {cont = "";} else {cont = num;}
  return (
    <div class={today ? "bg-gray-400" : ""} style='width: calc(100vw / 7)'>
      <div class='mb-auto text-right mr-4 mt-2 font-semibold'>{cont}</div>
      <For each={events}>
        {(item) => {
          return (
            <div class='text-xl ml-1 w-full bg-blue-300'>{`${item.title} - ${item.hour}:${item.minute}:${item.second}`}</div>
          );
        }}
      </For>
    </div>
  );
}

function handlingButton(d: Date, setDateState: Function, amount: number) {
  const _d = d;
  _d.setMonth(d.getMonth() + amount);
  setDateState([_d]);
}

function day(date: Date) {
  const _events: Record<number, Event[]> = {};
  events.forEach((item) => {
    if (item.year == date.getFullYear() && item.month == date.getMonth()+1) {
      if (_events[item.day] === undefined) {_events[item.day] = [];}
      _events[item.day].push(item);
    }
  });
  const fy = date.getFullYear();
  const fm = date.getMonth();
  const fd = date.getDate();
  const tmcmp = fm == new Date().getMonth() && fy == new Date().getFullYear();
  const _dateList: number[] = getDateList(date);
  const dateList = [];
  let i = 0;
  while (i <= _dateList.length) {
    const d = [];
    d.push(daySingle(_dateList[i], _dateList[i] === fd && tmcmp, _events[_dateList[i]]));
    let i2 = 1;
    while ((new Date(fy, fm, _dateList[i+i2])).getDay() != 0 && i+i2 < _dateList.length) {
      d.push(daySingle(_dateList[i+i2], _dateList[i+i2] === fd && tmcmp, _events[_dateList[i+i2]]));
      i2++;
    }
    if (d.length < 7 && i == 0) {
      let tmp = 0;
      const length = d.length;
      while (tmp <= 6-length) {
        d.unshift(daySingle());
        tmp++;
      }
    }
    i += i2;
    dateList.push(d);
  }
  dateList[dateList.length-1].shift();
  dateList[dateList.length-1].push(daySingle(_dateList[_dateList.length-1]+1, _dateList[_dateList.length-1]+1 === fd && tmcmp, _events[_dateList[_dateList.length-1]+1]));
  return (
    <For each={dateList}>
      {(item) => {
        return (
          <div class="flex flex-row h-1/5 border-gray-700 border-solid" style="border-top-width: 0.5px;">
            <For each={item}>{(item) => item}</For>
          </div>
        );
      }}
    </For>
  );
}

function App() {
  const dates = ["일", "월", "화", "수", "목", "금", "토"];
  const today = new Date();
  const [date, setDate] = createSignal([today]);

  return (
    <div>
      <div class="bg-white w-screen h-screen flex flex-col">
        <div class="bg-gray-300 w-screen flex flex-col h-32">
          <div class="m-auto flex flex-row gap-2">
            <button class='h-full w-6' onClick={()=>handlingButton(date()[0],setDate,-1)}><VsArrowLeft class="h-full w-full"/></button>
            <div class="text-4xl font-bold">{`${date()[0].getFullYear()}/${date()[0].getMonth()+1}`}</div>
            <button class='h-full w-6' onClick={()=>handlingButton(date()[0],setDate,1)}><VsArrowRight class="h-full w-full"/></button>
          </div>
          <div class="flex flex-row w-full h-1/3">
            <For each={dates}>{(item) => {
              return dayDisplay(item);
            }}</For>
          </div>
        </div>
        <div class="h-full flex flex-col">
          {day(date()[0])}
        </div>
      </div>
    </div>
  );
}

export default App;
