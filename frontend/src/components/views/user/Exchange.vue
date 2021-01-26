<template>
  <!-- Main content -->
  <section class="content">
    <!-- GitHub hint -->
    <div class="row justify-content-center">

      <!-- Info boxes -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-green"
                  :icon-classes="['fa', 'fa-plus']"
                  text="Euro -> Eurotoken"
                  v-bind:number="'1.00€ -> ' + rateE2T + 'ET'"></info-box>
      </div>
      <!-- /.col -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-blue"
                  :icon-classes="['fa', 'fa-minus']"
                  text="Eurotoken -> Euro"
                  v-bind:number="'1.00ET -> ' + rateT2E + '€'"></info-box>
      </div>
      <!-- /.col -->
    </div>
    <div class="row justify-content-center">
      <!-- fix for small devices only -->
      <div class="clearfix visible-sm-block"></div>

      <!-- /.col -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-yellow"
                  :icon-classes="['fa', 'fa-money']"
                  text="Token Balance"
                  v-bind:number="balance.toLocaleString() + 'ET'"></info-box>
      </div>
      <!-- /.col -->
    </div>
    <!-- /.row -->

    <div class="row">
      <div class="col-xs-12">
        <h2>Euro -> Eurotoken</h2>
      </div>
      <!-- with characthers -->
      <div class="col-md-6 col-xs-12">
        <label>Amount (Euro)</label>
        <div class="input-group">
          <span class="input-group-addon">
            <i class="fa fa-fw fa-eur" aria-hidden="true" ></i>
          </span>
          <input v-on:keyup.enter="initExchangeE2T" class="form-control" v-model="exchangeAmountE2T" type="text"
          placeholder="0.00" @keypress="onlyForCurrencyE2T" >
          <span class="input-group-addon"> : {{exchangeAmountE2TConverted}}ET</span>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 col-xs-12">
        <div class="form-group">
          <label>Payment Method</label>
          <select class="form-control">
            <option>Ideal</option>
            <option>option 2</option>
            <option>option 3</option>
            <option>option 4</option>
            <option>option 5</option>
          </select>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 col-xs-12">
        <a v-on:click="initExchangeE2T" class="btn btn-primary" role="button">Convert</a>
      </div>
    </div>

    <div class="row">
      <div class="col-xs-12">
        <h2>Eurotoken -> Euro</h2>
      </div>
      <!-- with characthers -->
      <div class="col-md-6 col-xs-12">
        <label>Amount (EuroToken)</label>
        <div class="input-group">
          <span class="input-group-addon">
            <i class="fa fa-fw fa-money" aria-hidden="true" ></i>
          </span>
          <input v-on:keyup.enter="initExchangeT2E" class="form-control" v-model="exchangeAmountT2E" type="text"
          placeholder="0.00" @keypress="onlyForCurrencyT2E" >
          <span class="input-group-addon"> : € {{exchangeAmountT2EConverted}}</span>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 col-xs-12">
        <div class="form-group">
          <label>IBAN</label>
          <input class="form-control" placeholder="NL91 ABNA 0417 1643 00" type="text">
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 col-xs-12">
        <a v-on:click="initExchangeT2E" class="btn btn-primary" role="button">Convert</a>
      </div>
    </div>

    <div class="col-xs-12">
      <h2>Open transactions</h2>
    </div>

    <div class="row">
      <div class="col-xs-12 table-responsive">
        <table
          role="grid"
          id="example1"
          class="table table-bordered table-striped dataTable">
          <thead>
            <tr role="row">
              <th colspan="1" rowspan="1" tabindex="0">Created</th>
              <th colspan="1" rowspan="1" tabindex="0">Amount</th>
              <th colspan="1" rowspan="1" tabindex="0">Price</th>
              <th colspan="1" rowspan="1" tabindex="0">ID</th>
              <th colspan="1" rowspan="1" tabindex="0">Status</th>
              <th colspan="1" rowspan="1" tabindex="0">Next Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in payments" class="even" role="row">

              <td>{{payment.created}}</td>
              <td>{{centToWhole(payment.payout_amount)}} {{payment.payout_currency}}</td>
              <td>{{centToWhole(payment.payment_amount)}} {{payment.payment_currency}}</td>
              <td>
                <!-- {{payment.payment_id}} -->
              </td>
              <td>
                <!-- {{payment.status_text}} -->
              </td>
              <td>
                <modal v-if="payment.payout_currency === 'eurotoken'" :name="payment.payment_id">
                  {{payment.status}}
                  <p v-if="payment.status === 0">
                  {{CREATE_get_connection_data(payment)}} <br>
                  <!-- {{payment.payment_transaction_data}} -->
                  <qrcode :value="CREATE_get_connection_data(payment)" :options="{ width: 200 }"></qrcode>
                  </p>
                  <p v-else-if="payment.status === 1">
                  <a @click="start_payment(payment.payment_id)" class="btn">Pay with Tikkie</a>
                  </p>
                  <p v-else-if="payment.status === 2">
                    <!-- {{payment}} -->
                    {{payment.payment_connection_data}}
                    <a @click="finish_payment(payment.payment_id)" class="btn">Payment complete</a>
                  </p>
                  <p v-else-if="payment.status === 3">
                    <!-- {{CREATE_get_connection_data(payment)}} -->
                    <qrcode :value="CREATE_get_connection_data(payment)" :options="{ width: 200 }"></qrcode>
                  </p>
                  <p v-else-if="payment.status === 4">
                  </p>
                  <a @click="hide(payment.payment_id)">Hide</a>
                </modal>
                <modal v-else-if="payment.payout_currency === 'euro'" :name="payment.payment_id">
                  {{payment.status}}
                  <p v-if="payment.status === 0">
                  ???
                  </p>
                  <p v-else-if="payment.status === 1">
                  ???
                  </p>
                  <p v-else-if="payment.status === 2">
                    {{DESTROY_payment_info(payment)}}
                    <qrcode :value="DESTROY_payment_info(payment)" :options="{ width: 200 }"></qrcode>
                  </p>
                  <p v-else-if="payment.status === 3">
                    ??
                  </p>
                  <p v-else-if="payment.status === 4">
                    ??
                  </p>
                  <a @click="hide(payment.payment_id)">Hide</a>
                </modal>
                <a @click="show(payment.payment_id)" :disabled="payment.status === 4" class="btn btn-primary" role="button">
                  {{next_action(payment)}}
                </a>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <th colspan="1" rowspan="1">Created</th>
              <th colspan="1" rowspan="1">Amount</th>
              <th colspan="1" rowspan="1">Price</th>
              <th colspan="1" rowspan="1">ID</th>
              <th colspan="1" rowspan="1">Status</th>
              <th colspan="1" rowspan="1">Next Action</th>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
    <!-- /.row -->
  </section>
  <!-- /.content -->
</template>

<script>
import Alert from '../../widgets/Alert'
import InfoBox from '../../widgets/InfoBox'
import ProcessInfoBox from '../../widgets/ProcessInfoBox'
const axios = require('axios')
// import $ from 'jquery'
// Require needed datatables modules
// require('datatables.net')
// require('datatables.net-bs')
const stores = require('../../shared_state.js')

export default {
  name: 'Exchange',
  components: {
    Alert,
    InfoBox,
    ProcessInfoBox
  },
  watch: {
    account: function () {
      this.updateTransactions()
    }
  },
  data: function() {
    return {
      payments: {},
      store: stores.store.state,
      exchangeAmountE2T: null,
      exchangeAmountT2E: null,
      balanceCent: 0,
      rateE2Tcent: 99,
      rateT2Ecent: 99,
      transactions: []
    }
  },
  computed: {
    account() {
      return this.store.account
    },
    exchangeAmountE2TConverted() {
      return (Math.floor(this.exchangeAmountE2T * this.rateE2Tcent) / 100).toFixed(2)
    },
    exchangeAmountT2EConverted() {
      return (Math.floor(this.exchangeAmountT2E * this.rateT2Ecent) / 100).toFixed(2)
    },
    rateE2T() {
      return (this.rateE2Tcent / 100).toFixed(2)
    },
    rateT2E() {
      return (this.rateT2Ecent / 100).toFixed(2)
    },
    balance() {
      return this.balanceCent / 100
    },
    isMobile () {
      return (window.innerWidth <= 800 && window.innerHeight <= 600)
    }
  },
  methods: {
    next_action(payment) {
      if (payment.payout_currency === 'eurotoken') {
        if (payment.status === 0) {
          return 'Connect to gateway'
        } else if (payment.status === 1) {
          return 'Select payment method'
        } else if (payment.status === 2) {
          return 'Waiting for payment'
        } else if (payment.status === 3) {
          return 'Connect to gateway'
        } else if (payment.status === 4) {
          return 'Payout done'
        }
      } else if (payment.payout_currency === 'euro') {
        if (payment.status === 0) {
          return '??'
        } else if (payment.status === 1) {
          return '??'
        } else if (payment.status === 2) {
          return 'Pay using IPv8'
        } else if (payment.status === 3) {
          return '??'
        } else if (payment.status === 4) {
          return 'Payout done'
        }
      }
    },
    clearPayments() {
      this.payments = {}
      this.$cookies.remove('payments')
    },
    DESTROY_payment_info(payment) {
      var data = {}
      data.payment_id = payment.payment_id
      data.amount = payment.payment_amount

      data.public_key = payment.gateway_connection_data.public_key
      data.ip = payment.gateway_connection_data.ip
      data.port = payment.gateway_connection_data.port
      return JSON.stringify(data)
    },
    CREATE_get_connection_data(payment) {
      var data = {}
      data.payment_id = payment.payment_id

      data.public_key = payment.gateway_connection_data.public_key
      data.ip = payment.gateway_connection_data.ip
      data.port = payment.gateway_connection_data.port
      return JSON.stringify(data)
    },
    show (paymentId) {
      this.$modal.show(paymentId)
    },
    hide (paymentId) {
      this.$modal.hide(paymentId)
    },
    set_payment(payment) {
      this.payments[payment.payment_id] = payment
      this.setPayments()
    },
    remove_payment(paymentId) {
      delete this.payments[paymentId]
      this.setPayments()
    },
    updatePayments() {
      if (this.$cookies.isKey('payments')) {
        this.payments = this.$cookies.get('payments')
      } else {
        this.payments = {}
      }
    },
    setPayments() {
      this.$cookies.set('payments', this.payments || {})
      this.updatePayments()
    },
    centToWhole (amount) {
      return (amount / 100).toFixed(2)
    },
    initExchangeE2T () {
      if (!this.exchangeAmountE2T) { return }
      let amount = this.exchangeAmountE2T * 100
      this.exchangeAmountE2T = null

      axios.post('/api/exchange/e2t/initiate', {
        collatoral_cent: amount
      }).then(response => {
        this.set_payment(response.data)
      })
        .then(this.updateTransactions())
    },
    start_payment (paymentId) {
      axios.post('/api/exchange/e2t/start_payment', {
        payment_id: paymentId
      }).then(response => {
        this.set_payment(response.data)
        this.transaction_status_changed(paymentId)
      })
    },
    finish_payment (paymentId) {
      // Fake callback
      axios.post('/api/exchange/e2t/finish_payment', {
        payment_id: paymentId
      }).then(response => {
        this.set_payment(response.data)
        this.transaction_status_changed(paymentId)
      })
    },
    initExchangeT2E () {
      if (!this.exchangeAmountT2E) { return }
      let amount = this.exchangeAmountT2E * 100
      // this.exchangeAmountT2E = null
      axios.post('/api/exchange/t2e/initiate', {
        token_amount_cent: amount,
        destination_iban: this.account
      }).then(response => {
        console.log(response.data)
        this.set_payment(response.data)
      }).then(this.updateTransactions())
    },
    confirmTransaction (paymentId, counterparty) {
      axios.post('/api/exchange/complete', {
        payment_id: paymentId,
        counterparty: counterparty
      }).then(response => console.log(response.data))
      axios.get('/api/exchange/payment', {
        params: {
          payment_id: paymentId
        }
      }).then(this.updateTransactions())
      // .then(this.updateBalance())
    },
    updateBalance () {
      axios.get('/api/transactions/balance', {
        params: {
          wallet: this.account
        }
      }).then(response => { this.balanceCent = response.data.balance })
    },
    updateTransactions () {
      for (let paymentId in this.payments) {
        axios.get('/api/exchange/status', {
          params: {
            'payment_id': paymentId
          }
        })
          .then(response => {
            if (this.payments[paymentId].status !== response.data.status) {
              this.set_payment(response.data)
              this.transaction_status_changed(paymentId)
            }
          })
          .catch(error => {
            if (error.response) {
              if (error.response.status === 404) {
                this.remove_payment(paymentId)
              }
            }
          })
      }
    },
    transaction_status_changed(paymentId) {
      const payment = this.payments[paymentId]
      const status = payment.status

      // hide all modals
      this.hide(paymentId)

      if (status === 0) { // CREATED = 0
        // trigger connection modal
      } else if (status === 1) { // PAYMENT_READY = 1
        // trigger tikkie modal
      } else if (status === 2) { // PAYMENT_PENDING = 2
        // update tikkie modal to waiting
      } else if (status === 3) { // PAYMENT_DONE = 3
        // show connection modal
      } else if (status === 4) { // PAYOUT_DONE = 4
        // show success toast
      }
    },
    onlyForCurrencyE2T ($event) {
      // console.log($event.keyCode); //keyCodes value
      let keyCode = ($event.keyCode ? $event.keyCode : $event.which)

      // only allow number and one dot
      if ((keyCode < 48 || keyCode > 57) && (keyCode !== 46 || this.exchangeAmountE2T.indexOf('.') !== -1)) { // 46 is dot
        $event.preventDefault()
      }

      // restrict to 2 decimal places
      if (this.exchangeAmountE2T != null && this.exchangeAmountE2T.indexOf('.') > -1 && (this.exchangeAmountE2T.split('.')[1].length > 1)) {
        $event.preventDefault()
      }
    },
    onlyForCurrencyT2E ($event) {
      // console.log($event.keyCode); //keyCodes value
      let keyCode = ($event.keyCode ? $event.keyCode : $event.which)

      // only allow number and one dot
      if ((keyCode < 48 || keyCode > 57) && (keyCode !== 46 || this.exchangeAmountT2E.indexOf('.') !== -1)) { // 46 is dot
        $event.preventDefault()
      }

      // restrict to 2 decimal places
      if (this.exchangeAmountT2E != null && this.exchangeAmountT2E.indexOf('.') > -1 && (this.exchangeAmountT2E.split('.')[1].length > 1)) {
        $event.preventDefault()
      }
    }
  },
  mounted () {
    axios.get('/api/exchange/e2t/rate')
      .then(response => { this.rateE2Tcent = response.data.token })
    axios.get('/api/exchange/t2e/rate')
      .then(response => { this.rateT2Ecent = response.data.eur })
    this.updatePayments()
    // this.updateBalance()
    this.timer = setInterval(this.updateTransactions, 1000)
  }
}
</script>
<style>
.info-box {
  cursor: pointer;
}
.info-box-content {
  text-align: center;
  vertical-align: middle;
  display: inherit;
}
.fullCanvas {
  width: 100%;
}

p { word-break: break-all }

</style>
