function drawGraphs(root) {
}

indicators = [
    { name : "Household incomes", url : "http://path.to.indicator" },
    { name : "Pit Latrines", url : "http://path.to.indicator" },
    { name : "Access to electricity", url : "http://path.to.indicator" },
    { name : "Household size", url : "http://path.to.indicator" },
    { name : "Access to transport", url : "http://path.to.indicator" },
    { name : "Water quality", url : "http://path.to.indicator" },
    { name : "Education Levels", url : "http://path.to.indicator" },
    { name : "Crime", url : "http://path.to.indicator" },
]

IndicatorList = function(ctx) {
    this.data = ctx.data; 
    this.rootElement = ctx.rootElement;
    this.currentView = this.data;
    this.init();
}

IndicatorList.prototype  = {

    init : function() {
        var me = this;
        d3.select("#searchBox")
            .on("keyup", function() {
                var searchbox = this;
                me.currentView = me.data.filter(function(el) {
                    var str = searchbox.value.toLowerCase();
                    return el.name.toLowerCase().indexOf(str) >= 0;
                });
                me.display(); 
            });
    },
    display : function() {
    
        var me = this;
        d3.select(this.rootElement)
            .selectAll("li")
            .remove();
        d3.select(this.rootElement)
           .selectAll("li")
           .data(me.currentView)
           .enter().append("li")
           .text(function(d) {
                return d.name;
           }); 

    }
}


