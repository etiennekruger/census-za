var po = org.polymaps;

indicators = [
    { name : "Household incomes", url : "/static/tiles/hh_income/{Z}/{X}/{Y}.png" },
    { name : "Pit Latrines", url : "/static/tiles/hh_density/{Z}/{X}/{Y}.png" },
    { name : "Access to electricity", url : "/static/tiles/hh_income/{Z}/{X}/{Y}.png" },
    { name : "Household size", url : "/static/tiles/hh_income/{Z}/{X}/{Y}.png" },
    { name : "Access to transport", url : "/static/tiles/hh_income/{Z}/{X}/{Y}.png" },
    { name : "Water quality", url : "/static/tiles/hh_income/{Z}/{X}/{Y}.png" },
    { name : "Education Levels", url : "/static/tiles/hh_income/{Z}/{X}/{Y}.png" },
    { name : "Crime", url : "/static/tiles/hh_income/{Z}/{X}/{Y}.png" },
]

cellListener = function(cell, data) {
    //d3.selectAll("#" + cell).text(data.name);
    mapping = {
        "tl" : tlMap,
        "tr" : trMap,
        "bl" : blMap,
        "br" : brMap,
    }

    var map = mapping[cell];
    console.log(map);
    map.draw(data.url);
}

MapCell = function(container) {
    this.container = container[0][0];
    this.map = po.map()
        .container(this.container.appendChild(po.svg("svg")))
        .center({lat: -28.6, lon: 23.2})
        .zoom(4)
        .zoomRange([4, 12])
        .add(po.interact())
        .add(po.hash());
}

MapCell.prototype = {
    draw : function(url) {

        if (this.layer1 !== undefined) {
            this.map.remove(this.layer1);
            this.map.remove(this.layer2);
            this.map.remove(this.layer3);
        }

        this.layer1 = po.image()
            .url(po.url("http://tilefarm.stamen.com/toner-no-labels/{Z}/{X}/{Y}.png"));
        this.layer2 = po.image()
            .url(po.url(url));
        this.layer3 = po.image()
            .url(po.url("http://tilefarm.stamen.com/toner-labels/{Z}/{X}/{Y}.png"));

        this.map.add(this.layer1);
        this.map.add(this.layer2);
        this.map.add(this.layer3);
    }
}

Grid4x4 = function(size, data) {
    this.size = size;
    this.data = data;
    this.observers = [];
}

Grid4x4.prototype = {
    draw : function(rootElement) {
        var me = this;
        var container = rootElement.append("div").classed("grid4x4 grid", true)
        container.selectAll("div")
            .data(["tl", "tr", "bl", "br"])
            .enter()
                .append("div")
                .classed("cell", true)
                .style("width", this.size + "px")
                .style("height", this.size + "px")
                .on("click", function(d) {
                    me.observers.forEach(function(listener) {
                        listener.call(me, d, me.data);
                    })
                });
        container.append("div").style("clear", "left");
    },
    registerListener : function(listener) {
        this.observers.push(listener);
    }
}

/*
    Object to draw a particular indicator
*/
IndicatorItem = function(data) {
    this.data = data;
}

IndicatorItem.prototype = {
    draw : function(rootElement) {
        var me = this;
        var container = rootElement.append("div")
        var grid4x4 = new Grid4x4(6, this.data);
        grid4x4.draw(container);
        grid4x4.registerListener(cellListener);
        container.append("span").text(this.data.name);
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


