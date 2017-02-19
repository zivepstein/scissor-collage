    // starting vertex marker
var DOT_COLOR = '#FCEBB6';
var DOT_OPACITY = 0.6;
var dot;

var POLY_A_COLOR = '#78C0A8';
var POLY_B_COLOR = '#F0A830';
var ERR_COLOR = 'red';
var SUCC_COLOR = 'green';
var RESET_COLOR = '#5E412F'
var POLY_HALF_OPACITY = 0.6;
var POLY_GHOST_OPACITY = 0.3;
var ALPHA = 0.01; // for iteratively calculating target area

var ANIMATION_TIME = 1;

var PADDING = 50;

$(function() {
    var aVertices;
    var bVertices;

    // set up two.js
    var canvas = document.getElementById('canvas');
    var two = new Two({
        width: $(canvas).width(),
        height: $(window).height()-500
    }).appendTo(canvas);


    var MAX_H;
    var MAX_W;
    var UNIT_WIDTH;


    var boxA;
    var boxB;
    var speedAX;
    var speedAY;
    var speedBX;
    var speedBY


    var stackPt;
    var area;

    var polyA ;

    var polyB;

    var polyCurr;

    var trisA = [];
    var trisB;

    var terminalTheta;
    var terminalX;
    var terminalY;

    var $canvas;
    var offset;

    reset();
    renderImage();

    function renderImage()
    {
        $.ajax({
            url: '/upload',
            dataType: 'json'
        }).done(function (data) {
            stackPt = new Two.Anchor((two.width-UNIT_WIDTH)/2, PADDING);
            $.each(data['spectrum'], function(i, d) {
                var height = d['area']/UNIT_WIDTH;
                var slice = makePoly([stackPt.x, stackPt.y,
                                        stackPt.x+UNIT_WIDTH, stackPt.y,
                                        stackPt.x+UNIT_WIDTH, stackPt.y+height,
                                        stackPt.x, stackPt.y+height]);
                slice.fill = d['fill'];
                stackPt.y += height;
                two.add(slice);
                two.update();
            });
            $.each(data['source-triangles'], function(i, t) {
                var tri = makePoly([t.a.x, t.a.y, t.b.x, t.b.y, t.c.x, t.c.y]);
                tri.fill = t.fill;
                tri = permuteTriVertices(tri);
                trisA.push(tri);
                two.add(tri);
                two.update();
            });
            $.each(data['target-triangles'], function(i, t) {
                var tri = makePoly([t.a.x, t.a.y, t.b.x, t.b.y, t.c.x, t.c.y]);
                tri.fill = t.fill;
                tri = permuteTriVertices(tri);
                trisB.push(tri);
                two.add(tri);
                two.update();
            });

            // two.bind('update', pause(ANIMATION_TIME, constructStack(0))).play();
        });
    }

    function reset(e)
    {
        two.width = $(canvas).width(),
        two.height = $(window).height()-150

        MAX_H = two.height/2;
        MAX_W = two.width/3;
        UNIT_WIDTH = MAX_W - 3*PADDING;

        $canvas = $("svg");
        $canvas.addClass('canvas');
        offset  = $canvas.offset();

        two.frameCount = 0;

        trisA = [];
        trisB = [];
        slices = [];

        polyA = two.makePath(0,0).noStroke();
        polyA.fill = POLY_A_COLOR;
        polyA.opacity = POLY_HALF_OPACITY;

        polyB = two.makePath(0,0).noStroke();
        polyB.fill = POLY_B_COLOR;
        polyB.opacity = POLY_HALF_OPACITY;

        polyCurr = polyA;
        

        two.update();
    }


    function constructStack(index) {
        return function() {
            var currTri = trisA[index];

            two.bind('update', straightenTri(currTri, ANIMATION_TIME, function() {
                var box = PolyK.GetAABB(toPolyK(currTri));
                console.log((two.width-box.width)/2-box.x);
                var longestSide = currTri.vertices[0].distanceTo(currTri.vertices[1]);
                two.bind('update', translate(currTri, ANIMATION_TIME, (two.width-box.width)/2-box.x, two.height-box.height-PADDING-box.y, function() {
                    two.bind('update', triToRect(currTri, function () {
                        two.bind('update', normalizeRect(currTri, UNIT_WIDTH, function() {
                            var box = PolyK.GetAABB(toPolyK(currTri));
                            two.bind('update', translate(currTri, ANIMATION_TIME, stackPt.x-box.x, stackPt.y-box.y, function(){
                                if(index < trisA.length-1)
                                {
                                    stackPt.y += box.height;
                                    constructStack(index+1)();
                                }
                                else
                                {
                                    two.bind('update', pause(ANIMATION_TIME, function () {
                                        var sliceHeight = area / UNIT_WIDTH;
                                        var stackY = PolyK.GetAABB(toPolyK(trisA[0])).y
                                        var stackX = PolyK.GetAABB(toPolyK(trisA[0])).x
                                        var currWidth = 0;
                                        for (var i = 0; i < trisB.length; i++)
                                        {
                                            var currTri = trisB[i];
                                            var sliceArea = PolyK.GetArea(toPolyK(currTri));
                                            var sliceWidth = sliceArea * UNIT_WIDTH / area;
                                            var slice = makePoly([stackX+UNIT_WIDTH-currWidth-sliceWidth, stackY,
                                                stackX+UNIT_WIDTH-currWidth, stackY,
                                                stackX+UNIT_WIDTH-currWidth, stackY+sliceHeight,
                                                stackX+UNIT_WIDTH-currWidth-sliceWidth, stackY+sliceHeight]);
                                            slice.fill = POLY_A_COLOR;
                                            slices.push(slice);
                                            two.add(slice);
                                            currWidth += sliceWidth;
                                        }
                                        for (var i = 0; i < trisA.length; i++)
                                        {
                                            two.remove(trisA[i]);
                                        }

                                        two.bind('update', pause(ANIMATION_TIME, deconstructStack(0))).play();
                                    })).play();
                                }
                            })).play();
                        })).play();
                    })).play();
                })).play();
            })).play();
        }
    }

    function deconstructStack(index) {
        return function() {
            var currTri = trisB[index];
            var slice = slices[index];

            var longestSide = currTri.vertices[0].distanceTo(currTri.vertices[1]);

            var sliceBox = PolyK.GetAABB(toPolyK(slice));

            two.bind('update', translate(slice, ANIMATION_TIME,
                (two.width-sliceBox.width)/2-sliceBox.x,
                two.height-sliceBox.height-PADDING-sliceBox.y,
                function() {
                two.bind('update', normalizeRect(slice, longestSide, function() {
                    two.bind('update', rectToTri(slice, currTri, function() {
                        two.bind('update', rotate(currTri, ANIMATION_TIME, terminalTheta, false, 0, 0, function() {
                            var triBox = PolyK.GetAABB(toPolyK(currTri));
                            two.bind('update', translate(currTri, ANIMATION_TIME, terminalX-triBox.x, terminalY-triBox.y, function() {
                                if(index < trisB.length-1)
                                {
                                    deconstructStack(index+1)();
                                }
                            })).play();
                        })).play();
                    })).play();
                })).play();
            })).play();
        }
    }

    function pause(frames, callback)
    {
        return function(frameCount) {
            if (frameCount <= frames) {}
            else
            {
                two.unbind('update', arguments.callee).pause();
                two.frameCount = 0;
                if (callback) callback();
            }
        };
    }



    function normalizeRect(p, w, callback)
    {
        var box = PolyK.GetAABB(toPolyK(p));

        if (box.width == w)
        {
            if (callback) return callback;
            else return;
        }
        else if (box.width > w)
        {
            return stackUp(p, w, callback);
        }
        else if (box.width * 2 < w)
        {
            return stackDown(p, w, callback);
        }
        else
        {
            var normalH = Math.abs(PolyK.GetArea(toPolyK(p))) / w;

            var penta = makePoly([box.x, box.y+box.height-normalH, box.x, box.y+box.height, box.x+box.width, box.y+box.height, box.x+w*normalH/box.height, box.y+normalH, box.x+(box.height-normalH)*w/box.height, box.y+box.height-normalH]);
            penta.fill = p.fill;
            two.add(penta);

            var smallTri = makePoly([box.x, box.y, box.x, box.y+box.height-normalH, box.x+(box.height-normalH)*w/box.height, box.y+box.height-normalH]);
            smallTri.fill = p.fill;
            two.add(smallTri);

            var bigTri = makePoly([box.x, box.y, box.x+box.width, box.y, box.x+w*normalH/box.height, box.y+normalH]);
            bigTri.fill = p.fill;
            two.add(bigTri);

            two.remove(p);

            return translate(smallTri, ANIMATION_TIME, w*normalH/box.height, normalH, function() {
                two.bind('update', translate(bigTri, ANIMATION_TIME, (box.height-normalH)*w/box.height, box.height-normalH, function() {
                    two.remove(smallTri, bigTri, penta);
                    p.vertices = makeVertices([box.x, box.y+box.height-normalH, box.x+w, box.y+box.height-normalH, box.x+w, box.y+box.height, box.x, box.y+box.height]);
                    two.add(p);
                    if (callback) callback();
                })).play();
            });
        }
    }

    function stackUp(p, w, callback)
    {
        var box = PolyK.GetAABB(toPolyK(p));
        var pivotX = box.x+box.width/2;
        var pivotY = box.y;
        
        var left = makePoly([pivotX, pivotY, box.x, box.y, box.x, box.y+box.height, pivotX, box.y+box.height]);
        left.fill = p.fill;
        two.add(left);

        var right = makePoly([pivotX, pivotY, box.x+box.width, box.y, box.x+box.width, box.y+box.height, pivotX, box.y+box.height]);
        right.fill = p.fill;
        two.add(right);

        two.remove(p);

        return rotate(right, ANIMATION_TIME, Math.PI, true, pivotX, pivotY, function() {
            two.remove(left, right);
            p.vertices = makeVertices([box.x, box.y-box.height, pivotX, box.y-box.height, pivotX, box.y+box.height, box.x, box.y+box.height]);
            two.add(p);
            two.bind('update', normalizeRect(p, w, callback)).play();
        });

    }

    function stackDown(p, w, callback)
    {
        var box = PolyK.GetAABB(toPolyK(p));
        var pivotX = box.x+box.width;
        var pivotY = box.y+box.height/2;
        
        var top = makePoly([box.x, box.y, pivotX, box.y, pivotX, pivotY, box.x, pivotY]);
        top.fill = p.fill;
        two.add(top);

        var bottom = makePoly([box.x, pivotY, pivotX, pivotY, pivotX, pivotY+box.height/2, box.x, pivotY+box.height/2]);
        bottom.fill = p.fill;
        two.add(bottom);

        two.remove(p);

        return rotate(top, ANIMATION_TIME, Math.PI, false, pivotX, pivotY, function() {
            two.remove(top, bottom);
            p.vertices = makeVertices([box.x, pivotY, pivotX+box.width, pivotY, pivotX+box.width, box.y+box.height, box.x, box.y+box.height]);
            two.add(p);
            two.bind('update', normalizeRect(p, w, callback)).play();
        });

    }

    function triangulate()
    {
        var polyKA = toPolyK(polyA);
        var polyKB = toPolyK(polyB);

        var trA = PolyK.Triangulate(polyKA);
        for(var i = 0; i < trA.length; i+=3)
        {
            var triangle = [polyKA[trA[i]*2], polyKA[trA[i]*2+1],
                polyKA[trA[i+1]*2], polyKA[trA[i+1]*2+1],
                polyKA[trA[i+2]*2], polyKA[trA[i+2]*2+1]];
            var t = makePoly(triangle);
            t.fill = POLY_A_COLOR;
            t = permuteTriVertices(t);
            trisA.push(t);
            
            var tGhost = makePoly(triangle);
            tGhost.fill = POLY_A_COLOR;
            tGhost.opacity = POLY_GHOST_OPACITY;

            two.add(tGhost, t);

            UNIT_WIDTH = Math.min(UNIT_WIDTH, 2*t.vertices[0].distanceTo(t.vertices[1])-1);
        }

        two.remove(polyA);


        var trB = PolyK.Triangulate(polyKB);
        for(var i = 0; i < trB.length; i+=3)
        {
            var triangle = [polyKB[trB[i]*2], polyKB[trB[i]*2+1],
                polyKB[trB[i+1]*2], polyKB[trB[i+1]*2+1],
                polyKB[trB[i+2]*2], polyKB[trB[i+2]*2+1]];
            var t = makePoly(triangle);
            t = permuteTriVertices(t);
            trisB.push(t);

            var tGhost = makePoly(triangle);
            tGhost.fill = POLY_B_COLOR;
            tGhost.opacity = POLY_GHOST_OPACITY;

            two.add(tGhost);
        }

        two.remove(polyB);
    }

    function makePoly(p) {
        points = [];
        for (var i = 0; i < p.length; i+=2) {
            var x = p[i];
            var y = p[i + 1];
            points.push(new Two.Anchor(x, y));
        }

        var path = new Two.Path(points, true);
        path.noStroke();

        return path;

    }

    function triToRect(t, callback)
    {
        var color = t.fill;

        var a = t.vertices[0];
        var b = t.vertices[1];
        var c = t.vertices[2];
        var Y = (c.y+a.y)/2;
        var rightX = (c.x+a.x)/2;
        var leftX = (c.x+b.x)/2;

        var trap = makePoly([a.x, a.y, b.x, b.y, leftX, Y, rightX, Y]);
        trap.fill = color;
        two.add(trap);

        var lt = [c.x, Y, leftX, Y, c.x, c.y];
        var lbox = PolyK.GetAABB(lt);
        var leftTri = makePoly(lt);
        leftTri.fill = color;
        two.add(leftTri);

        var rt = [rightX, Y, c.x, Y, c.x, c.y];
        var rbox = PolyK.GetAABB(rt);
        var rightTri = makePoly(rt);
        rightTri.fill = color;
        two.add(rightTri)

        two.remove(t);

        return rotate(leftTri, ANIMATION_TIME, Math.PI, true, leftX, Y, function() {
            two.bind('update', rotate(rightTri, ANIMATION_TIME,Math.PI, false, rightX, Y, function() {
                two.remove(trap, rightTri, leftTri);
                t.vertices = makeVertices([a.x, a.y, a.x, Y, b.x, Y, b.x, b.y]);
                two.add(t);
                if(callback) callback();
            })).play();
        });
    }

    function rectToTri(r, t, callback)
    {
        var box = PolyK.GetAABB(toPolyK(r));
        var triBox = PolyK.GetAABB(toPolyK(t));
        terminalX = triBox.x;
        terminalY = triBox.y;

        (straightenTri(t, 1))(1);
        (translate(t, 1, box.x-t.vertices[1].x, box.y+box.height-t.vertices[1].y))(1);

        var color = r.fill;

        var a = t.vertices[0];
        var b = t.vertices[1];
        var c = t.vertices[2];
        var Y = (c.y+a.y)/2;
        var rightX = (c.x+a.x)/2;
        var leftX = (c.x+b.x)/2;

        var trap = makePoly([a.x, a.y, b.x, b.y, leftX, Y, rightX, Y]);
        trap.fill = color;
        two.add(trap);

        var lt = [leftX, Y, b.x, b.y, b.x, Y];
        var lbox = PolyK.GetAABB(lt);
        var leftTri = makePoly(lt);
        leftTri.fill = color;
        two.add(leftTri);

        var rt = [rightX, Y, a.x, Y, a.x, a.y];
        var rbox = PolyK.GetAABB(rt);
        var rightTri = makePoly(rt);
        rightTri.fill = color;
        two.add(rightTri)

        two.remove(r);

        return rotate(leftTri, ANIMATION_TIME, Math.PI, false, leftX, Y, function() {
            two.bind('update', rotate(rightTri, ANIMATION_TIME,Math.PI, true, rightX, Y, function() {
                two.remove(trap, rightTri, leftTri);
                t.fill = r.fill;
                two.add(t);
                if(callback) callback();
            })).play();
        });
    }

    function makeVertices(p)
    {
        v = [];
        for(var i = 0; i < p.length; i += 2)
        {
            v.push(new Two.Anchor(p[i], p[i+1]));
        }
        return v;
    }

    function straightenTri(t, frames, callback)
    {
        var a = t.vertices[0];
        var b = t.vertices[1];
        var c = t.vertices[2];
        terminalTheta = Math.atan((b.y-a.y)/(b.x-a.x));
        var p = PolyK.rotate(toPolyK(t), terminalTheta);
        if (p[5] > p[1])
        {
            terminalTheta += Math.PI;
        }

        return rotate(t, frames, terminalTheta, true, 0, 0, function() {
            if (callback) callback();
        });
    }

    function permuteTriVertices(t)
    {
        var a = t.vertices[0];
        var b = t.vertices[1];
        var c = t.vertices[2];
        var ab = a.distanceTo(b);
        var ac = a.distanceTo(c);
        var bc = b.distanceTo(c);
        var max = Math.max(ab, ac, bc);
       
        var perm;
        if (max == ab)
        {
            perm = [a,b,c];
        }
        else if (max == ac)
        {
            perm = [c,a,b];
        }
        else
        {
            perm = [b,c,a];
        }

        t.vertices = perm;
        return t;
    }

    function toPolyK(p)
    {
        return $.map(p.vertices, function(v) {
            return [v.x, v.y];
        })
    }

    function translate(p, frames, x, y, callback)
    {
        var speedX = x / frames;
        var speedY = y / frames;

        return function(frameCount) {
            if (frameCount <= frames)
            {
                p.vertices = makeVertices(PolyK.translate(toPolyK(p), speedX, speedY));
            }
            else
            {
                two.unbind('update', arguments.callee).pause();
                two.frameCount = 0;
                if(callback) callback();
            }
        }
    }

    function rotate(p, frames, theta, ccw, x, y, callback)
    {
        var speedTheta = theta / frames;
        if (!ccw) speedTheta *= -1;

        return function(frameCount) {
            if (frameCount <= frames)
            {
                p.vertices = makeVertices(PolyK.rotate(toPolyK(p), speedTheta, x, y));
            }
            else
            {
                two.unbind('update', arguments.callee).pause();
                two.frameCount = 0;
                if(callback) callback();
            }
        }
    }
});
