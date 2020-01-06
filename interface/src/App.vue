<template>
  <div id="app">
    <b-container fluid>
      <b-row :no-gutters=true>
        <b-col cols="2">
          <div class="control-panel"></div>
        </b-col>
        <b-col cols="10">
          <b-row :no-gutters=true>
            <b-col cols="8">
              <div class="map">
                <Map></Map>
              </div>
              <div class="test"></div>
            </b-col>
            <b-col cols="4">
              <div class="docs"></div>
            </b-col>
          </b-row>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import Map from './components/Map.vue'
export default {
  name: "app",
  components: {
    Map
  }
};
</script>

<style lang="scss">
html,
body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow-y: hidden;
}
* {
  border: 0.1px red solid;
}
#app {
  width: 100%;
  height: 100%;

  .control-panel {
    height: 1000px;
    background-color: pink;
  }

  .map {
    width: 100%;
    height: 600px;
  }

  .test {
    width: 100%;
    height: 400px;
  }

  .docs {
    height: 1000px;
  }
}
</style>
