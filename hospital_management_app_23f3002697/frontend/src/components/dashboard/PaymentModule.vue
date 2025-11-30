<template>
  <div class="card card-soft">
    <div class="card-body">
      <h6 class="fw-bold mb-3">Treatment Payment</h6>
      <form @submit.prevent="handleSubmit" novalidate>
        <div class="mb-3">
          <label class="form-label">Cardholder Name</label>
          <input
            type="text"
            class="form-control rounded-3"
            v-model.trim="form.name"
            :class="{ 'is-invalid': errors.name }"
            required
          />
          <div class="invalid-feedback">{{ errors.name }}</div>
        </div>
        <div class="mb-3">
          <label class="form-label">Card Number</label>
          <input
            type="text"
            class="form-control rounded-3"
            v-model.trim="form.card"
            maxlength="19"
            :class="{ 'is-invalid': errors.card }"
            placeholder="XXXX XXXX XXXX XXXX"
            required
          />
          <div class="invalid-feedback">{{ errors.card }}</div>
        </div>
        <div class="row">
          <div class="col-6 mb-3">
            <label class="form-label">Expiry</label>
            <input
              type="text"
              class="form-control rounded-3"
              v-model.trim="form.expiry"
              placeholder="MM/YY"
              :class="{ 'is-invalid': errors.expiry }"
              required
            />
            <div class="invalid-feedback">{{ errors.expiry }}</div>
          </div>
          <div class="col-6 mb-3">
            <label class="form-label">CVV</label>
            <input
              type="password"
              class="form-control rounded-3"
              v-model.trim="form.cvv"
              maxlength="4"
              autocomplete="off"
              :class="{ 'is-invalid': errors.cvv }"
              required
            />
            <div class="invalid-feedback">{{ errors.cvv }}</div>
          </div>
        </div>
        <button class="btn btn-primary w-100 rounded-pill" type="submit">
          Pay $120.00
        </button>
      </form>
      <div v-if="successMessage" class="alert alert-success rounded-3 mt-3 mb-0">
        {{ successMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';

const form = reactive({
  name: '',
  card: '',
  expiry: '',
  cvv: ''
});

const errors = reactive({
  name: '',
  card: '',
  expiry: '',
  cvv: ''
});

const successMessage = ref('');

const validate = () => {
  errors.name = form.name ? '' : 'Name is required';
  errors.card = /^\d{4}\s?\d{4}\s?\d{4}\s?\d{4}$/.test(form.card)
    ? ''
    : 'Enter a valid card number';
  errors.expiry = /^(0[1-9]|1[0-2])\/\d{2}$/.test(form.expiry)
    ? ''
    : 'Use MM/YY format';
  errors.cvv = /^\d{3,4}$/.test(form.cvv) ? '' : 'Invalid CVV';

  return !errors.name && !errors.card && !errors.expiry && !errors.cvv;
};

const handleSubmit = () => {
  if (!validate()) return;
  successMessage.value = 'Payment processed securely via SerenityCare sandbox.';
  setTimeout(() => (successMessage.value = ''), 4000);
};
</script>

