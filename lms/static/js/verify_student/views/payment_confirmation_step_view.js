/**
 * View for the "payment confirmation" step of the payment/verification flow.
 */
var edx = edx || {};

(function( $ ) {
    'use strict';

    edx.verify_student = edx.verify_student || {};

    // The "Verify Later" button goes directly to the dashboard,
    // The "Verify Now" button reloads this page with the "skip-first-step"
    // flag set.  This allows the user to navigate back to the confirmation
    // if he/she wants to.
    // For this reason, we don't need any custom click handlers here.
    edx.verify_student.PaymentConfirmationStepView = edx.verify_student.StepView.extend({
        postRender: function() {
            // Track the user's decision to verify immediately
            $( "#verify_now_button" ).on( 'click', function() {
                window.analytics.track( 'edx.bi.user.verification.immediate', {
                    category: 'verification'
                });
            });

            // Track the user's decision to defer their verification
            $( "#verify_later_button" ).on( 'click', function() {
                window.analytics.track( 'edx.bi.user.verification.deferred', {
                    category: 'verification'
                });
            });
        }
    });

})( jQuery );
