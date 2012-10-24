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

/*
    Object to draw a particular indicator
*/
IndicatorItem = function(data) {
    this.data = data;
}

IndicatorItem.prototype = {
    draw : function(rootElement) {
        //rootElement.text(this.data.name);
        var me = this;
        rootElement.append("a")
            .attr("href", function() {
                return me.data.url;
            })
            .text(this.data.name);
    }
}

/*
    Widget to draw a list of indicators
*/
IndicatorList = function(ctx) {
    this.data = ctx.data; 
    this.rootElement = ctx.rootElement;
    this.currentView = this.data;
    this.init();
}

IndicatorList.prototype = {

    init : function() {
        var me = this;
        // TODO this code might actually move out of here
        // we could wire it up outside of this object
        d3.select("#searchBox")
            .on("keyup", function() {
                var searchbox = this;
                var str = searchbox.value.toLowerCase();
                me.filter(str);
            });
    },
    filter : function(str) {
        // Filter the displayed list of indicators
        var me = this;
        me.currentView = me.data.filter(function(el) {
            return el.name.toLowerCase().indexOf(str) >= 0;
        });
        me.display(); 
    },
    display : function() {
        // Display the updated list of indicators
        var me = this;
        d3.select(this.rootElement)
            .selectAll("li")
            .remove();
        d3.select(this.rootElement)
            .selectAll("li")
            .data(me.currentView)
            .enter().append("li")
            .each(function(d) {
                var item = new IndicatorItem(d);
                item.draw(d3.select(this));
            })
    }
}


