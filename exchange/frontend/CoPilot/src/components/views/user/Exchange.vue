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
                  number="1.01€/T"></info-box>
      </div>
      <!-- /.col -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-blue"
                  :icon-classes="['fa', 'fa-minus']"
                  text="Eurotoken -> Euro"
                  number="0.99T/€"></info-box>
      </div>
      <!-- /.col -->
    </div>
    <div class="row justify-content-center">
      <!-- fix for small devices only -->
      <div class="clearfix visible-sm-block"></div>

      <!-- /.col -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-yellow"
                  :icon-classes="['fa', 'fa-eur']"
                  text="Current Balance"
                  number="2,000"></info-box>
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
        <label>Amount (EuroToken)</label>
        <div class="input-group">
          <span class="input-group-addon">
            <i class="fa fa-fw fa-eur" aria-hidden="true"></i>
          </span>
          <input class="form-control" type="text">
          <span class="input-group-addon">.00</span>
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
      <div class="col-xs-12">
        <h2>Eurotoken -> Euro</h2>
      </div>
      <!-- with characthers -->
      <div class="col-md-6 col-xs-12">
        <label>Amount (EuroToken)</label>
        <div class="input-group">
          <span class="input-group-addon">
            <i class="fa fa-fw fa-eur" aria-hidden="true"></i>
          </span>
          <input class="form-control" type="text">
          <span class="input-group-addon" placeholder="12">.00</span>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 col-xs-12">
        <div class="form-group">
          <label>IBAN</label>
          <div class="input-group">
            <input class="form-control" placeholder="NL91 ABNA 0417 1643 00" type="text">
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-xs-12">
        <h2>Exchange History</h2>
      </div>
      <div class="col-md-6 col-xs-12">
        <table
          role="grid"
          id="example1"
          class="table table-bordered table-striped dataTable">
          <thead>
            <tr role="row">
              <th style="width: 167px;" colspan="1" rowspan="1" tabindex="0"> Date </th>
              <th style="width: 182px;" colspan="1" rowspan="1" tabindex="0"> Amount </th>
              <th style="width: 142px;" colspan="1" rowspan="1" tabindex="0"> In/Out </th>
              <th style="width: 101px;" colspan="1" rowspan="1" tabindex="0"> Description </th>
              <th style="width: 101px;" colspan="1" rowspan="1" tabindex="0"> Status </th>
            </tr>
          </thead>
          <tbody>
            <tr class="even" role="row">
              <td>2020 May 01 15:19</td>
              <td>2,567.00 €T</td>
              <td>In</td>
              <td>Salary April</td>
              <td>Confirmed</td>
            </tr>
            <tr class="odd" role="row">
              <td>2020 April 01 12:48</td>
              <td>2,567.00 €T</td>
              <td>In</td>
              <td>Salary March</td>
              <td>Confirmed</td>
            </tr>
            <tr class="even" role="row">
              <td>2020 March 02 11:34</td>
              <td>2,567.00 €T</td>
              <td>In</td>
              <td>Salary February</td>
              <td>Confirmed</td>
            </tr>
            <tr class="odd" role="row">
              <td>2020 February 02 8:23</td>
              <td>2,567.00 €T</td>
              <td>In</td>
              <td>Salary January</td>
              <td>Confirmed</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <th colspan="1" rowspan="1">Date</th>
              <th colspan="1" rowspan="1">Amount</th>
              <th colspan="1" rowspan="1">In/Out</th>
              <th colspan="1" rowspan="1">Description</th>
              <th colspan="1" rowspan="1">Status</th>
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
import Chart from 'chart.js'
import Alert from '../../widgets/Alert'
import InfoBox from '../../widgets/InfoBox'
import ProcessInfoBox from '../../widgets/ProcessInfoBox'

export default {
  name: 'Wallet',
  components: {
    Alert,
    InfoBox,
    ProcessInfoBox
  },
  data () {
    return {
      generateRandomNumbers (numbers, max, min) {
        var a = []
        for (var i = 0; i < numbers; i++) {
          a.push(Math.floor(Math.random() * (max - min + 1)) + max)
        }
        return a
      }
    }
  },
  computed: {
    coPilotNumbers () {
      return this.generateRandomNumbers(12, 1000000, 10000)
    },
    personalNumbers () {
      return this.generateRandomNumbers(12, 1000000, 10000)
    },
    isMobile () {
      return (window.innerWidth <= 800 && window.innerHeight <= 600)
    }
  },
  mounted () {
    this.$nextTick(() => {
      var ctx = document.getElementById('trafficBar').getContext('2d')
      var config = {
        type: 'line',
        data: {
          labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
          datasets: [{
            label: 'CoPilot',
            fill: false,
            borderColor: '#284184',
            pointBackgroundColor: '#284184',
            backgroundColor: 'rgba(0, 0, 0, 0)',
            data: this.coPilotNumbers
          }, {
            label: 'Personal Site',
            borderColor: '#4BC0C0',
            pointBackgroundColor: '#4BC0C0',
            backgroundColor: 'rgba(0, 0, 0, 0)',
            data: this.personalNumbers
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: !this.isMobile,
          legend: {
            position: 'bottom',
            display: true
          },
          tooltips: {
            mode: 'label',
            xPadding: 10,
            yPadding: 10,
            bodySpacing: 10
          }
        }
      }

      new Chart(ctx, config) // eslint-disable-line no-new

      var pieChartCanvas = document.getElementById('languagePie').getContext('2d')
      var pieConfig = {
        type: 'pie',
        data: {
          labels: ['HTML', 'JavaScript', 'CSS'],
          datasets: [{
            data: [56.6, 37.7, 4.1],
            backgroundColor: ['#00a65a', '#f39c12', '#00c0ef'],
            hoverBackgroundColor: ['#00a65a', '#f39c12', '#00c0ef']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: !this.isMobile,
          legend: {
            position: 'bottom',
            display: true
          }
        }
      }

      new Chart(pieChartCanvas, pieConfig) // eslint-disable-line no-new
    })
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
</style>
