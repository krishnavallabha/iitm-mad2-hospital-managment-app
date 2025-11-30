<template>
  <div class="appointment-calendar">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h5 class="fw-bold mb-1">{{ currentMonthYear }}</h5>
        <p class="text-muted small mb-0">{{ viewMode === 'month' ? 'Monthly View' : 'Weekly View' }}</p>
      </div>
        <div class="d-flex gap-2 flex-wrap">
        <button
          class="btn btn-outline-secondary rounded-pill btn-sm"
          @click="previousPeriod"
        >
          <i class="bi bi-chevron-left"></i>
        </button>
        <button
          class="btn btn-outline-primary rounded-pill btn-sm"
          @click="goToToday"
        >
          <span class="d-none d-sm-inline">Today</span>
          <span class="d-sm-none">Now</span>
        </button>
        <button
          class="btn btn-outline-secondary rounded-pill btn-sm"
          @click="nextPeriod"
        >
          <i class="bi bi-chevron-right"></i>
        </button>
        <div class="btn-group">
          <button
            class="btn rounded-pill btn-sm"
            :class="viewMode === 'month' ? 'btn-primary' : 'btn-outline-primary'"
            @click="viewMode = 'month'"
          >
            <span class="d-none d-sm-inline">Month</span>
            <span class="d-sm-none">M</span>
          </button>
          <button
            class="btn rounded-pill btn-sm"
            :class="viewMode === 'week' ? 'btn-primary' : 'btn-outline-primary'"
            @click="viewMode = 'week'"
          >
            <span class="d-none d-sm-inline">Week</span>
            <span class="d-sm-none">W</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Month View -->
    <div v-if="viewMode === 'month'" class="calendar-month">
      <div class="calendar-header">
        <div
          v-for="day in weekDays"
          :key="day"
          class="calendar-day-header"
        >
          {{ day }}
        </div>
      </div>
      <div class="calendar-grid">
        <div
          v-for="(date, index) in calendarDays"
          :key="index"
          class="calendar-day"
          :class="{
            'other-month': !date.isCurrentMonth,
            'today': date.isToday,
            'has-appointments': date.appointmentCount > 0
          }"
          @click="selectDate(date.date)"
        >
          <div class="day-number">{{ date.day }}</div>
          <div class="appointments-preview">
            <span
              v-for="(apt, idx) in date.appointments.slice(0, 3)"
              :key="apt.id"
              class="appointment-badge"
              :class="getStatusClass(apt.status)"
              :title="`${apt.time} - ${apt.patient_name || apt.doctor_name}`"
            >
              {{ apt.time }}
            </span>
            <span
              v-if="date.appointmentCount > 3"
              class="more-appointments"
            >
              +{{ date.appointmentCount - 3 }} more
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Week View -->
    <div v-else class="calendar-week">
      <div class="week-header">
        <div class="time-column"></div>
        <div
          v-for="date in weekDates"
          :key="date.date"
          class="week-day-header"
          :class="{ 'today': date.isToday }"
        >
          <div class="day-name">{{ date.dayName }}</div>
          <div class="day-number">{{ date.day }}</div>
        </div>
      </div>
      <div class="week-body">
        <div class="time-column">
          <div
            v-for="hour in hours"
            :key="hour"
            class="time-slot"
          >
            {{ formatHour(hour) }}
          </div>
        </div>
        <div
          v-for="date in weekDates"
          :key="date.date"
          class="week-day-column"
        >
          <div
            v-for="hour in hours"
            :key="hour"
            class="time-cell"
            @click="selectTimeSlot(date.date, hour)"
          >
            <div
              v-for="apt in getAppointmentsForSlot(date.date, hour)"
              :key="apt.id"
              class="appointment-block"
              :class="getStatusClass(apt.status)"
              :style="getAppointmentStyle(apt)"
              @click.stop="selectAppointment(apt)"
            >
              <div class="appointment-time">{{ apt.time }}</div>
              <div class="appointment-title">{{ apt.patient_name || apt.doctor_name }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointment Details Modal -->
    <div
      v-if="selectedAppointment"
      class="modal fade show d-block"
      style="background-color: rgba(0, 0, 0, 0.5);"
      @click.self="selectedAppointment = null"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rounded-4">
          <div class="modal-header">
            <h5 class="modal-title">Appointment Details</h5>
            <button
              type="button"
              class="btn-close"
              @click="selectedAppointment = null"
            ></button>
          </div>
          <div class="modal-body">
            <p><strong>Date:</strong> {{ formatDate(selectedAppointment.date) }}</p>
            <p><strong>Time:</strong> {{ selectedAppointment.time }}</p>
            <p><strong>Status:</strong> 
              <span class="badge" :class="getStatusClass(selectedAppointment.status)">
                {{ selectedAppointment.status }}
              </span>
            </p>
            <p v-if="selectedAppointment.patient_name">
              <strong>Patient:</strong> {{ selectedAppointment.patient_name }}
            </p>
            <p v-if="selectedAppointment.doctor_name">
              <strong>Doctor:</strong> {{ selectedAppointment.doctor_name }}
            </p>
            <p v-if="selectedAppointment.reason">
              <strong>Reason:</strong> {{ selectedAppointment.reason }}
            </p>
          </div>
          <div class="modal-footer">
            <button
              class="btn btn-secondary rounded-pill"
              @click="selectedAppointment = null"
            >
              Close
            </button>
            <slot name="actions" :appointment="selectedAppointment"></slot>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  appointments: {
    type: Array,
    default: () => []
  },
  initialDate: {
    type: Date,
    default: () => new Date()
  }
});

const emit = defineEmits(['date-selected', 'appointment-selected', 'time-slot-selected']);

const currentDate = ref(new Date(props.initialDate));
const viewMode = ref('month');
const selectedAppointment = ref(null);

const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const hours = Array.from({ length: 12 }, (_, i) => i + 8); // 8 AM to 7 PM

const currentMonthYear = computed(() => {
  return currentDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
});

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const startDate = new Date(firstDay);
  startDate.setDate(startDate.getDate() - startDate.getDay());
  
  const days = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    
    const dateStr = date.toISOString().split('T')[0];
    const dayAppointments = props.appointments.filter(apt => {
      const aptDate = new Date(apt.appointment_date || apt.date);
      return aptDate.toISOString().split('T')[0] === dateStr;
    });
    
    days.push({
      date: new Date(date),
      day: date.getDate(),
      isCurrentMonth: date.getMonth() === month,
      isToday: date.getTime() === today.getTime(),
      appointments: dayAppointments.map(apt => ({
        ...apt,
        time: formatTime(apt.appointment_time || apt.time)
      })),
      appointmentCount: dayAppointments.length
    });
  }
  
  return days;
});

const weekDates = computed(() => {
  const startOfWeek = new Date(currentDate.value);
  startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay());
  
  const dates = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(startOfWeek);
    date.setDate(startOfWeek.getDate() + i);
    
    dates.push({
      date: date.toISOString().split('T')[0],
      day: date.getDate(),
      dayName: weekDays[date.getDay()],
      isToday: date.getTime() === today.getTime()
    });
  }
  
  return dates;
});

const previousPeriod = () => {
  if (viewMode.value === 'month') {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1);
  } else {
    currentDate.value = new Date(currentDate.value);
    currentDate.value.setDate(currentDate.value.getDate() - 7);
  }
};

const nextPeriod = () => {
  if (viewMode.value === 'month') {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1);
  } else {
    currentDate.value = new Date(currentDate.value);
    currentDate.value.setDate(currentDate.value.getDate() + 7);
  }
};

const goToToday = () => {
  currentDate.value = new Date();
};

const selectDate = (date) => {
  emit('date-selected', date);
};

const selectTimeSlot = (date, hour) => {
  emit('time-slot-selected', { date, hour });
};

const selectAppointment = (appointment) => {
  selectedAppointment.value = appointment;
  emit('appointment-selected', appointment);
};

const getAppointmentsForSlot = (date, hour) => {
  return props.appointments.filter(apt => {
    const aptDate = new Date(apt.appointment_date || apt.date);
    const dateStr = aptDate.toISOString().split('T')[0];
    if (dateStr !== date) return false;
    
    const aptTime = apt.appointment_time || apt.time;
    const aptHour = typeof aptTime === 'string' 
      ? parseInt(aptTime.split(':')[0])
      : aptTime.getHours();
    
    return aptHour === hour;
  });
};

const getAppointmentStyle = (apt) => {
  const startTime = typeof apt.appointment_time === 'string'
    ? apt.appointment_time
    : apt.appointment_time.toTimeString().slice(0, 5);
  const [hours, minutes] = startTime.split(':').map(Number);
  const top = ((hours - 8) * 60 + minutes) * (100 / (12 * 60));
  const duration = 30; // Assume 30 min appointments
  const height = (duration / 60) * (100 / 12);
  
  return {
    top: `${top}%`,
    height: `${height}%`
  };
};

const getStatusClass = (status) => {
  const classes = {
    'Booked': 'bg-primary-subtle text-primary border-primary',
    'Completed': 'bg-success-subtle text-success border-success',
    'Cancelled': 'bg-danger-subtle text-danger border-danger'
  };
  return classes[status] || 'bg-secondary-subtle text-secondary';
};

const formatTime = (time) => {
  if (!time) return '';
  if (typeof time === 'string') {
    const [h, m] = time.split(':');
    const hour = parseInt(h);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${m} ${ampm}`;
  }
  return time.toTimeString().slice(0, 5);
};

const formatHour = (hour) => {
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  return `${displayHour}:00 ${ampm}`;
};

const formatDate = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
};
</script>

<style scoped>
.appointment-calendar {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.calendar-day-header {
  text-align: center;
  font-weight: 600;
  color: #6c757d;
  padding: 0.5rem;
  font-size: 0.875rem;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
}

.calendar-day {
  min-height: 100px;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.calendar-day:hover {
  background: #f8f9fa;
  border-color: #6c63ff;
}

.calendar-day.other-month {
  opacity: 0.4;
  background: #f8f9fa;
}

.calendar-day.today {
  border: 2px solid #6c63ff;
  background: #f0f0ff;
}

.calendar-day.has-appointments {
  border-left: 4px solid #6c63ff;
}

.day-number {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.appointments-preview {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.appointment-badge {
  font-size: 0.75rem;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  border: 1px solid;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.more-appointments {
  font-size: 0.7rem;
  color: #6c757d;
  font-style: italic;
}

/* Week View */
.week-header {
  display: grid;
  grid-template-columns: 80px repeat(7, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.time-column {
  width: 80px;
}

.week-day-header {
  text-align: center;
  padding: 0.5rem;
  border-radius: 0.5rem;
  background: #f8f9fa;
}

.week-day-header.today {
  background: #f0f0ff;
  border: 2px solid #6c63ff;
}

.day-name {
  font-size: 0.75rem;
  color: #6c757d;
  text-transform: uppercase;
}

.day-number {
  font-size: 1.25rem;
  font-weight: 600;
}

.week-body {
  display: grid;
  grid-template-columns: 80px repeat(7, 1fr);
  gap: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  overflow: hidden;
}

.time-column {
  display: flex;
  flex-direction: column;
}

.time-slot {
  height: 60px;
  border-bottom: 1px solid #dee2e6;
  padding: 0.25rem;
  font-size: 0.75rem;
  color: #6c757d;
  display: flex;
  align-items: flex-start;
}

.week-day-column {
  display: flex;
  flex-direction: column;
  border-left: 1px solid #dee2e6;
}

.time-cell {
  height: 60px;
  border-bottom: 1px solid #dee2e6;
  position: relative;
  cursor: pointer;
  transition: background 0.2s;
}

.time-cell:hover {
  background: #f8f9fa;
}

.appointment-block {
  position: absolute;
  left: 2px;
  right: 2px;
  border-radius: 0.25rem;
  padding: 0.25rem;
  font-size: 0.75rem;
  border: 1px solid;
  cursor: pointer;
  z-index: 10;
  overflow: hidden;
}

.appointment-time {
  font-weight: 600;
  font-size: 0.7rem;
}

.appointment-title {
  font-size: 0.65rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Mobile Responsive */
@media (max-width: 767.98px) {
  .appointment-calendar {
    padding: 1rem;
  }
  
  .calendar-grid {
    gap: 0.25rem;
  }
  
  .calendar-day {
    min-height: 80px;
    padding: 0.25rem;
    font-size: 0.75rem;
  }
  
  .day-number {
    font-size: 0.875rem;
  }
  
  .appointment-badge {
    font-size: 0.65rem;
    padding: 0.1rem 0.2rem;
  }
  
  .week-header,
  .week-body {
    grid-template-columns: 60px repeat(7, 1fr);
    gap: 0.25rem;
    font-size: 0.75rem;
  }
  
  .time-column {
    width: 60px;
    font-size: 0.7rem;
  }
  
  .time-slot,
  .time-cell {
    height: 50px;
  }
  
  .d-flex.gap-2 {
    flex-wrap: wrap;
  }
  
  .d-flex.gap-2 .btn {
    flex: 1 1 auto;
    min-width: 60px;
  }
}

@media (max-width: 575.98px) {
  .appointment-calendar {
    padding: 0.75rem;
  }
  
  .calendar-day {
    min-height: 60px;
    padding: 0.2rem;
  }
  
  .day-number {
    font-size: 0.75rem;
  }
  
  .calendar-header,
  .calendar-grid {
    gap: 0.2rem;
  }
  
  .calendar-day-header {
    font-size: 0.7rem;
    padding: 0.25rem;
  }
  
  .week-header,
  .week-body {
    grid-template-columns: 50px repeat(7, 1fr);
    gap: 0.2rem;
  }
  
  .time-column {
    width: 50px;
    font-size: 0.65rem;
  }
  
  .time-slot,
  .time-cell {
    height: 40px;
  }
  
  h5 {
    font-size: 1rem;
  }
  
  .d-flex.gap-2 {
    flex-direction: column;
  }
  
  .d-flex.gap-2 .btn-group {
    width: 100%;
  }
  
  .d-flex.gap-2 .btn-group .btn {
    flex: 1;
  }
}
</style>

