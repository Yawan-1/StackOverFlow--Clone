var modal = document.getElementById("pop-Modal");


var btn = document.getElementById("open-popup");

var closeBtn = document.getElementById("close-popup")

btn.onclick = function() {
    modal.style.display = "block";
}

closeBtn.onclick = function() {
    modal.style.display = "none";
}

window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}    



    document.addEventListener('DOMContentLoaded', function() {
        window.addEventListener('load', function() {

        var popUpModal = document.getElementById("pop-Modal");

            getting = document.getElementsByTagName("details");
            $('.Commentator').on('click',function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'commenter'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'commenter') {
                                $('#badge-card-next').html(
                                    `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__bronze">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge3"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Commenter</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{countComments|percentage}}%;"></div>
                                    </div>`
                                );
                            popUpModal.style.display = "none";
                        }
                    }
                })
            })
            getting = document.getElementsByTagName("details");
            $('.altruist').on('click', function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'altruist'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'altruist') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__bronze">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge3"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Alturist</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.archaeologist').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'archaeologist'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'archaeologist') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__bronze">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge3"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Archaelogist</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{profileData.post_edit_inactive_for_six_month}}%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })

// HERE

            $('.autobiographer').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'autobiographer'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'autobiographer') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__bronze">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge3"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Autobiographer</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })

            $('.benefactor').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'benefactor'},
                    dataType: 'json',
                    method: 'get',
                    async: true,
                    success: function(response) {
                        if (response.action == 'benefactor') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__bronze">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge3"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Benefactor</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })

            $('.citizen_duty').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'citizen_duty'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'citizen_duty') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__bronze">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge3"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Citizen Patrol</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
        })
        var popUpModal = document.getElementById("pop-Modal");

            $('.civic_duty').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'civic_duty'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'civic_duty') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__bronze">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge2"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Civic Duty</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{countVotes}}%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.copy_editor').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'copy_editor'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'copy_editor') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Copy Editor</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{profileData.posts_edited_counter|advanced_percentage:500}}%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.critic').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'critic'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'critic') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Critic</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.custodian').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'custodian'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'custodian') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Custodian</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.deputy').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'deputy'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'deputy') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__silver">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge2"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Deputy</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{profileData.helpful_flags_counter|advanced_percentage:80}}%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.disciplned').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'disciplned'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'disciplned') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__bronze">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge3"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Disciplned</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.excavator').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'excavator'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'excavator') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__silver">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge2"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Excavator</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.investor').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'investor'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'investor') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__silver">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge2"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Investor</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.marshal').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'marshal'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'marshal') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Marhal</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{profileData.helpful_flags_counter}}%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.necromancer').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'necromancer'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'necromancer') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Necromancer</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.peer_pressure').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'peer_pressure'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'peer_pressure') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Peer Pressure</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.promoter').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'promoter'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'promoter') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__bronze">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge3"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Promoter</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.proofreader').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'proofreader'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'proofreader') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Peer Pressure</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{profileData.suggested_Edit_counter}}%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.refiner').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'refiner'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'refiner') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__silver">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge2"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Refiner</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{profileData.Refiner_Illuminator_TagPostCounter|advanced_percentage:50}}%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.revival').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'revival'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'revival') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Revival</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.self_learner').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'self_learner'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'self_learner') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Self Lerner</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.strunk_white').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'strunk_white'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'strunk_white') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Strunk & White</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{profileData.posts_edited_counter|advanced_percentage:80}}%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.suffrage').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'suffrage'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'suffrage') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Suffrage</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{totalVotes|advanced_percentage:30}}%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.teacher').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'teacher'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'teacher') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Teacher</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: 0%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
            $('.vox_populi').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {'submit': 'vox_populi'},
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'vox_populi') {
                                $('#badge-card-next').html(
                                     `<div id="badge-card-next" class="s-progress s-progress__badge s-progress__gold">
                                        <div class="d-flex gs12 gsx m0 s-progress--label">
                                            <div class="flex--item mr0 s-badge--image badge1"></div>
                                            <div class="d-flex flex__center fl1 s-badge--label">Vox Populi</div>
                                        </div>
                                        <div class="s-progress--bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="80" style="width: {{totalVotes|advanced_percentage:40}}%;"></div>
                                    </div>`
                                );
                        popUpModal.style.display = "none";
                        }
                    }
                })
            })
    })