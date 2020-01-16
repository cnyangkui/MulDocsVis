<template>
  <div class="container">
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
.container {
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
