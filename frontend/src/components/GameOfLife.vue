<template>
  <vue-p5 v-on="{setup, draw, mouseclicked}"></vue-p5>
</template>

<script>
  import VueP5 from 'vue-p5';

  let w;
  let width = 512;
  let height = 512;
  let columns;
  let rows;
  let board;
  let next;

  function init(sketch) {
    for (let i = 0; i < columns; i++) {
      for (let j = 0; j < rows; j++) {
        // Lining the edges with 0s
        if (i === 0 || j === 0 || i === columns-1 || j === rows-1) board[i][j] = 0;
        // Filling the rest randomly
        // else board[i][j] = Math.floor(p5.random(2));
        else board[i][j] = sketch.floor(sketch.random(2));
        next[i][j] = 0;
      }
    }
  }

function generate() {
  // Loop through every spot in our 2D array and check spots neighbors
  for (let x = 1; x < columns - 1; x++) {
    for (let y = 1; y < rows - 1; y++) {
      // Add up all the states in a 3x3 surrounding grid
      let neighbors = 0;
      for (let i = -1; i <= 1; i++) {
        for (let j = -1; j <= 1; j++) {
          neighbors += board[x+i][y+j];
        }
      }

      // A little trick to subtract the current cell's state since
      // we added it in the above loop
      neighbors -= board[x][y];
      // Rules of Life
      if      ((board[x][y] === 1) && (neighbors <  2))  next[x][y] = 0;           // Loneliness
      else if ((board[x][y] === 1) && (neighbors >  3))  next[x][y] = 0;           // Overpopulation
      else if ((board[x][y] === 0) && (neighbors === 3)) next[x][y] = 1;           // Reproduction
      else                                               next[x][y] = board[x][y]; // Stasis
    }
  }

  // Swap!
  let temp = board;
  board = next;
  next = temp;
}

  export default {
    name: "GameOfLife",
    methods: {
      setup (sketch) {
        // sketch.background('green');
        // sketch.text('Hello p5!', 20, 20);

        sketch.createCanvas(width, height);
        w = 16;
        // Calculate columns and rows
        // columns = sketch.floor(width / w);
        // rows = sketch.floor(height / w);
        columns = sketch.floor(sketch.width / w);
        rows = sketch.floor(sketch.height / w);
        // Wacky way to make a 2D array is JS
        board = new Array(columns);
        for (let i = 0; i < columns; i++) {
          board[i] = new Array(rows);
        }
        // Going to use multiple 2D arrays and swap them
        next = new Array(columns);
        for (let i = 0; i < columns; i++) {
          next[i] = new Array(rows);
        }
        init(sketch);
      },
      draw (sketch) {
        sketch.background(255);
        generate();
        for ( let i = 0; i < columns;i++) {
          for ( let j = 0; j < rows;j++) {
            if ((board[i][j] === 1)) sketch.fill(0);
            else sketch.fill(255);
            sketch.stroke(0);
            sketch.rect(i * w, j * w, w-1, w-1);
          }
        }
        this.$socket.emit('new-label', {label_map: board});
      },
      keypressed (sketch) {
        init(sketch)
      },
      mouseclicked (sketch) {
        init(sketch)
      }
    },
    components: {
      VueP5
    }
  }
</script>

<style scoped>

</style>
