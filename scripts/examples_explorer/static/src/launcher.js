
function show_source(example, data){
  // TODO: probably don't need this global var anymore..
  window.selected_example = example;
  var jqxhr = $.get( "api/source", {'id': example}, function(data) {

      $('#source_text_dlg')
        .modal('setting', 'closable', false)
        .modal('show');

        $("#code_filename").html(data.name);
        // Take the code and put it into the codemirror editor.
        window.cm.getDoc().setValue(data.source);
    })
      .fail(function() {
        alert( "Error trying to retrieve file source code" );
      });

}


function show_loading(itemid){
  $("#"+itemid+"_loader").addClass('active');
  $("#"+itemid+"_loader div").addClass('active');
}

function hide_loading(itemid){
    $("#"+itemid+"_loader").removeClass('active');
    $("#"+itemid+"_loader div").removeClass('active');
}

function enable_status(id, status){
  $("#"+id+"_status").removeClass('gray');
  $("#"+id+"_status").removeClass('red');
  $("#"+id+"_status").addClass('green');
  // $("#"+id+"_status").text(status);
  $("#"+id+"_seen").html(status);
  $("#"+id+"_seen").visible();
}


function register_example(example, status){
  if (example.status!=''){
    enable_status(example.id, example.status);
  }

  if (example.bug_report!=''){
    jQuery("#"+example.id+"_bugged").attr("data-title", "Error Reported" );
    jQuery("#"+example.id+"_bugged").attr("data-content", example.bug_report );
    $("#"+example.id+"_bugged").popup({hoverable: true,});
    $("#"+example.id+"_bugged").html(example.bug_report);
    $("#"+example.id+"_bugged").html("errored");
    $("#"+example.id+"_bugged").visible();
  }
}

var CommentBox = React.createClass({
  render: function() {
    return (
      <div className="commentBox">
        <h1>Comments</h1>
        <CommentList data={this.props.data} />
        <CommentForm />
      </div>
    );
  }
});


var Example = React.createClass({
  rawMarkup: function() {
    var rawMarkup = marked(this.props.children.toString(), {sanitize: true});
    return { __html: rawMarkup };
  },

  handleClick: function(exampleid) {
    return run_example(exampleid);
  },

  handleClickFeedback: function(exampleid){
    return ask_feedback(exampleid);
  },

  handleClickSourceCode: function(exampleid, data){
    show_source(exampleid, data);
  },

  render: function() {
    var status_id = this.props.data.id + "_status";
    var seen_id = this.props.data.id + "_seen";
    var bugged_id = this.props.data.id + "_bugged";
    var loader_id = this.props.data.id + "_loader";
    var img_id = this.props.data.id + "_img";
    var status_btn_classes = "ui button playbtn";
    var btn_label = "Play";
    var icon_classes = "play icon"
    var seen_lbl_style = {visibility: "hidden"}
    var bugged_lbl_style = {top: 20+"px", visibility: "hidden"}

    // if (this.props.data.status == 'seen'){
    //   status_btn_classes = status_btn_classes + ' green'
    //   btn_label = 'Replay';
    //   icon_classes = 'repeat icon';
    //   seen_lbl_style = {}
    // }

    var boundClick = this.handleClick.bind(this, this.props.data.id);
    var boundClickFeedback = this.handleClickFeedback.bind(this, this.props.data.id);
    var boundClickSourcecode = this.handleClickSourceCode.bind(this, this.props.data.id, this.props.data);


    var return_default_image = function(){
      console.log("CALLED ON ERROR", "#"+img_id, '/static/images/logo.png');
      $("#"+img_id).src='/static/images/logo.png';
    }
    console.log("SOURCE", this.props.data.image_file);
    return ( //React.createElement("div",
      // {
      //   id: this.props.data.id,
      // },
      <div id={this.props.data.id} className="segment card">
      <div id={loader_id} className="ui dimmer">
        <div className="ui active loader">Loading...</div>
      </div>
        <div className="blurring dimmable image">
          <div className="ui dimmer">
            <div className="content">
              <div className="center">

                <button id={status_id} className={status_btn_classes}  onClick={boundClick}>
                  <i className={icon_classes}></i>{btn_label}
                </button>
                <button onClick={boundClickSourcecode}
                className="ui left circular facebook icon button" style={{float: "left"}}>
                  <i className="code icon"></i>
                </button>
                <button onClick={boundClickFeedback}
                className="ui left circular yellow icon button" style={{float: "right"}}>
                  <i className="bug icon"></i>
                </button>
              </div>
            </div>
          </div>
          <img id={img_id} className="ui wireframe image example_img" style={{height: 190+"px"}} src={this.props.data.image_file} alt="Image not found" onError={return_default_image}></img>
        </div>


        <div className="ui green label extra">
          <div id={seen_id} className="floating left ui green label" style={seen_lbl_style}>{this.props.status}</div>
          <div id={bugged_id} className="floating ui red label" style={bugged_lbl_style}>bugged</div>
          {this.props.shortname}
        </div>
      </div>
    );
  }
});

function register_examples(examples){
  if (examples!=undefined){
    for (var i = 0; i < examples.length; i++) {
      register_example(examples[i]);
    }
  }

}

var FilesList = React.createClass({
  render: function() {
    var data = this.props.data;
    setTimeout(function(){register_examples(data);}, 200);
    var exampleNodes = this.props.data.map(function(example) {
      return (
        <Example key={example.id} shortname={example.shortname} data={example} status={example.status}>

        </Example>
      );
    });
    return (
        <div className="ui three special cards examples_list">
          {exampleNodes}
        </div>
    );
  }
});

var FoldersList = React.createClass({
  render: function() {
    var foldersNodes = this.props.folders.map(function(folder) {
      return (
        <div className="ui center aligned basic segment">
          <div className="ui horizontal divider">
            <i className="folder open icon"></i>
            {folder.shortname}
            <div className="ui teal label">{folder.files.length}</div>
          </div>
          <div>
            <FilesList data={folder.files} key={folder.id}/>
          </div>
        </div>
      );
    });

    return (
      <div>
        <div className="ui center aligned basic segment">
          <div className="ui center aligned basic segment">
            <div className="ui horizontal divider">
              <i className="folder open icon"></i>
              root
              <div className="ui teal label">{this.props.root.files.length}</div>
            </div>
            <div>
              <FilesList data={this.props.root.files} key={this.props.root.id}/>
            </div>
          </div>
          {foldersNodes}
        </div>
      </div>
    );
  }
});

var FolderSummary = React.createClass({
  render: function() {
    var folders = [];
    var new_folder;
    for (var key in this.props.session.folders){
      new_folder = this.props.session.folders[key];
      new_folder.type = this.props.type;
      folders.push(new_folder)
    }

    var foldersNodes = folders.map(function(folder) {
      var files_seen = [];
      var files_reported = [];
      var files = [];
      var file;
      var folders = [];

      for (var key in folder.folders){
        folder.folders[key].type = folder.type;
        folders.push(folder.folders[key])
      }

      for (var i = 0; i < folder.files.length; i++) {
        file = folder.files[i];
        files.push(files);
        if (file.status!=''){
          files_seen.push(file);
          if (file.bug_report!=''){
            files_reported.push(file);
          }
        }
      }

      var reportedNodes = files_reported.map(function(file) {
        var files_filed = [];
        return (
          <div className="item">
            <i className="large github middle aligned icon"></i>
            <div className="content">
              <a className="header">file.shortname</a>
              <div className="description">file.bug_report</div>
            </div>
          </div>
        );
      });

      return (
        <div className="ui center aligned basic segment">
          <div className="ui horizontal divider">
            <i className="folder open icon"></i>
            {folder.shortname}
            <div className="ui green label">{files_seen.length}</div>
            <div className="ui red label">{files_reported.length}</div>
            <div className="ui teal label">{files.length}</div>
          </div>
          <div className="ui relaxed divided list">
          FOL
            {reportedNodes}
          </div>
        </div>
        );
    });

    return (
      <div>
        <div className="ui center aligned basic segment">
          {foldersNodes}
        </div>
      </div>
    );
  }
});

var FoldersSummary = React.createClass({
  render: function() {
    var folders = [];
    var new_folder;
    for (var key in this.props.session.folders){

      new_folder = this.props.session.folders[key];
      new_folder.subfolders = [];
      // new_folder.type = this.props.type;


      for (var key in new_folder.folders){
        new_folder.subfolders.push(new_folder.folders[key])
      }
      folders.push(new_folder);
    }

    var foldersNodes = folders.map(function(folder) {
      var files_seen = [];
      var files_reported = [];
      var files = [];
      var file;
      var folders = [];
      // console.log("foold", folder.type, folder, folder.id, folder.files);

      for (var key in folder.folders){
        folder.folders[key].type = folder.type;
        folders.push(folder.folders[key])
      }

      for (var i = 0; i < folder.files.length; i++) {
        file = folder.files[i];
        files.push(files);
        if (file.status!=''){
          files_seen.push(file);
          if (file.bug_report!=''){
            files_reported.push(file);
          }
        }
      }

      for (var key in folder.folders){
        // folder.folders[key].type = folder.type;
        // folders.push(folder.folders[key])
        var subfolder = folder.folders[key]
        for (var i = 0; i < subfolder.files.length; i++) {
          file = subfolder.files[i];
          files.push(files);
          if (file.status!=''){
            files_seen.push(file);
            if (file.bug_report!=''){
              files_reported.push(file);
            }
          }
        }
      }

      var reportedNodes = files_reported.map(function(file) {
        var files_filed = [];
        return (
          <div className="item">
            <i className="large bug middle aligned red icon"></i>
            <div className="content">
              <a className="header"><h3>{file.bug_report_type}</h3>{file.shortname}</a>
              <div className="description">{file.bug_report}</div>
            </div>
          </div>
        );
      });


      return (
          <div className="ui center aligned basic segment">
            <div className="ui horizontal divider">
              <i className="folder open icon"></i>
              {folder.shortname}
              <div className="ui green label">{files_seen.length}</div>
              <div className="ui red label">{files_reported.length}</div>
              <div className="ui teal label">{files.length}</div>
            </div>
            <div className="ui relaxed divided list">
              {reportedNodes}
            </div>
          </div>
        );
    });

    return (
      <div>
        <div className="ui center aligned basic segment">

          {foldersNodes}
        </div>
      </div>
    );
  }
});

// tutorial21.js
var FolderBox = React.createClass({
  loadFilesFromServer: function() {
    console.log("CALLED");
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {data: {files:[], folders: [], shortname: '', id: 'none'}};
  },
  componentDidMount: function() {
    this.loadFilesFromServer();
    // setInterval(this.loadCommentsFromServer, this.props.pollInterval);
  },
  render: function() {
    var folders = [];
    for (var key in this.state.data.folders){
      folders.push(this.state.data.folders[key])
    }

    return (
      <div className="ui dividing">
        <div className="ui left labeled button" tabIndex="0">
          <a className="ui basic right pointing label">
          <h2>

            {this.state.data.shortname}
          </h2>
          </a>
          <div className="ui play button" style={{padding: 15+"px"}}>
            <i className="play icon"></i> Run All
          </div>
        </div>
        <FoldersList key={this.state.data.id} root={this.state.data} folders={folders} shortname={this.state.data.shortname}/>
      </div>
    );
  }
});


function get_folder_info_from_hash(root_folder){
  var files_seen = [];
  var files_reported = [];
  var files = [];
  var file;
  var folders = [];

  for (var i = 0; i < root_folder.files.length; i++) {
    files.push(root_folder.files[i]);
  }
  for (var key in root_folder.folders){
    var folder = root_folder.folders[key];
    folders.push(folder);

    for (var i = 0; i < folder.files.length; i++) {
      file = folder.files[i];
      files.push(file);
      if (file.status!=''){
        files_seen.push(file);
        if (file.bug_report!=''){
          files_reported.push(file);
        }
      }
    }
  }
  return {"folders": folders, "files": files, "files_seen": files_seen, "files_reported": files_reported}
}

var FolderBoxData = React.createClass({

  render: function() {
    folder_info = get_folder_info_from_hash(this.props.data);


    return (
      <div>
          <h1 className="ui right floated header">{this.props.data.shortname}</h1>

          <button className="ui labeled icon button" >
            <i className="play icon"></i>
            Run All
          </button>
          <a style={{marginRight: 30+"px"}}></a>
          <a id="folder_files_seen" className="ui green tag label">{folder_info.files_seen.length} files seen</a>
          <a id="folder_bugs" className="ui red tag label">{folder_info.files_reported.length} known bugs</a>
          <a id="folder_total_files" className="ui yellow tag label">{folder_info.files.length} total files</a>

        <FoldersList key={this.props.data.id} root={this.props.data} folders={folder_info.folders} shortname={this.props.data.shortname}/>
      </div>
    );
  }
});

var SessionBox = React.createClass({
  render: function() {
    return (
      <div>

        <h1 className="ui right floated header">Session Details</h1>
        <button className="ui labeled icon button" >
          <i className="play icon"></i>
          Run All
        </button>
        <button className="ui labeled icon button" >
          <i className="file icon"></i>
          Export
        </button>

        <a style={{marginRight: 30+"px"}}></a>
        <div className="ui center aligned basic segment">
          <div className="ui horizontal divider"></div>
          <div className="ui horizontal divider">
            <i className="bug icon"></i>
            Bugs Reported
            <div className="ui teal label">{this.props.session.bugs.length}</div>
          </div>
        </div>
        <FoldersSummary key="session" session={this.props.session} type='main'/>
      </div>
    );
  }
});

function show_session(){
  var path = "/api/session";

  $.ajax({
    url: path,
    dataType: 'json',
    cache: false,
    success: function(data) {
      ReactDOM.render(
        <SessionBox session={data} />,
        document.getElementById('main-container')
      );

      // TODO: should select the session button and unselect all the others

      setTimeout(reset_semantic, 100);
    }.bind(this),
    error: function(xhr, status, err) {
      console.error(this.props.url, status, err.toString());
    }.bind(this)
  });
}

function show_new_section(folder){
  var path = "/api/session?folder="+folder;
  ReactDOM.render(
    <FolderBox url={path} />,
    document.getElementById('main-container')
  );
  setTimeout(reset_semantic, 100);

  // React.render(React.createElement(FolderBox, {url: path}), document.getElementById('main-container'));
}
// show_new_section('app')

function select_folder(folder_id){

  $(".examples-root").invisible();

  $("#" + folder_id).visible();

  $(".examples-menu-item").removeClass("active");
  $(".examples-menu-item").removeClass("teal");

  $("#"+folder_id+"_menu_item").addClass("teal");
  $("#"+folder_id+"_menu_item").addClass("active");
  $("#"+folder_id+"_menu_label").addClass("teal");
}


function update_stats(folder){
  var path = "/api/session?folder=" + window.current_folder;

  $.ajax({url: path, dataType: 'json', cache: false,
    success: function(data) {
        $("#"+data.id+"_menu_label").html(data.seen_files_count+" /"+data.total_files_count);
        $("#folder_files_seen").html(data.seen_files_count + " files seen");

    }.bind(this),
    error: function(xhr, status, err) {
      console.error(this.props.url, status, err.toString());
    }.bind(this)
  });

}

function update_new_section(folder){
  var path = "/api/session?folder="+folder;
  window.current_folder = folder;
  $.ajax({
    url: path,
    dataType: 'json',
    cache: false,
    success: function(data) {
      ReactDOM.render(
        <FolderBoxData data={data} />,
        document.getElementById('main-container')
      );

      select_folder(data.id);

      setTimeout(reset_semantic, 100);
    }.bind(this),
    error: function(xhr, status, err) {
      console.error(this.props.url, status, err.toString());
    }.bind(this)
  });

}
